import json
import random  # Adicionado para rolagens aleatórias no combate
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Max, Q
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.core.cache import cache
from .models import Rolagem, Personagem, Mesa, Item, Combate, ParticipanteCombate, AcaoCombate, Missao, MissaoPersonagem, Notificacao
from .forms import PersonagemForm, MesaForm, ItemForm
from .messaging import publicar_rolagem
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


# --- REQUISITO (viii): PAINEL DE ESTATÍSTICAS (Aggregation + Cache de Baixo Nível) ---

@login_required
def painel_estatisticas(request):
    """Gera inteligência de dados processada com estratégia de cache em banco."""
    stats = cache.get('painel_estatisticas_data')
    
    if not stats:
        stats = {
            'total_rolagens': Rolagem.objects.count(),
            'media_geral': Rolagem.objects.aggregate(Avg('resultado'))['resultado__avg'] or 0,
            'maior_valor': Rolagem.objects.aggregate(Max('resultado'))['resultado__max'] or 0,
            'rank_jogadores': list(Rolagem.objects.values('jogador_nome')
                                            .annotate(total=Count('id'))
                                            .order_by('-total')[:5])
        }
        cache.set('painel_estatisticas_data', stats, 300)

    return render(request, 'lobby/estatisticas.html', {'stats': stats})


# --- LOBBY PRINCIPAL / DASHBOARD ---

@login_required
def dashboard(request):
    mesas = Mesa.objects.all().order_by('-data_criacao')
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    
    return render(request, 'lobby/index.html', {
        'mesas': mesas,
        'personagens': personagens
    })


# --- REQUISITO (vi): SISTEMA DE ROLLBACK ---

@login_required
def rollback_rolagem(request, pk):
    rolagem = get_object_or_404(Rolagem, pk=pk)
    
    if rolagem.mesa and rolagem.mesa.mestre != request.user:
        return HttpResponseForbidden("Apenas o Mestre desta mesa pode alterar o destino dos dados.")

    if request.method == "POST":
        novo_resultado = request.POST.get('novo_resultado')
        motivo = request.POST.get('motivo')

        if novo_resultado and motivo:
            rolagem.resultado_anterior = rolagem.resultado
            rolagem.resultado = int(novo_resultado)
            rolagem.editado = True
            rolagem.motivo_edicao = motivo
            rolagem.save()
            cache.delete('painel_estatisticas_data')
            messages.success(request, "O tecido do destino foi alterado! Rolagem modificada com sucesso.")
            return redirect('dashboard')

    return render(request, 'lobby/form_rollback.html', {'rolagem': rolagem})


# --- ENDPOINTS DA API DE ROLAGENS ---

@csrf_exempt
@login_required
def salvar_rolagem(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            personagem_id = data.get('personagem_id')
            mesa_id = data.get('mesa_id')
            
            personagem = None
            if personagem_id:
                personagem = Personagem.objects.get(id=personagem_id, usuario=request.user, ativo=True)
            
            mesa = None
            if mesa_id:
                mesa = Mesa.objects.get(id=mesa_id)
            elif personagem and personagem.mesa:
                mesa = personagem.mesa

            rolagem = Rolagem.objects.create(
                personagem=personagem,
                mesa=mesa,
                jogador_nome=data.get('jogador_nome', request.user.username),
                tipo_dado=data.get('tipo_dado', 'D20'),
                resultado=int(data.get('resultado'))
            )
            
            evento_dados = {
                'id': rolagem.id,
                'jogador_nome': rolagem.jogador_nome,
                'tipo_dado': rolagem.tipo_dado,
                'resultado': rolagem.resultado,
                'data_hora': timezone.localtime(rolagem.data_hora).strftime('%d/%m/%Y %H:%M:%S')
            }
            publicar_rolagem(evento_dados)
            cache.delete('painel_estatisticas_data')

            return JsonResponse({
                'status': 'sucesso',
                'id': rolagem.id,
                'jogador': rolagem.jogador_nome,
                'resultado': rolagem.resultado
            })
        except Exception as e:
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'erro', 'message': 'Método inválido'}, status=405)


@login_required
def listar_rolagens(request):
    rolagens = Rolagem.objects.all().order_by('-data_hora')[:30]
    data = [{
        'id': r.id,
        'jogador': r.jogador_nome,
        'tipo_dado': r.tipo_dado,
        'resultado': r.resultado,
        'editado': r.editado,
        'resultado_anterior': r.resultado_anterior,
        'motivo': r.motivo_edicao,
        'data_hora': timezone.localtime(r.data_hora).strftime('%H:%M:%S')
    } for r in rolagens]
    return JsonResponse({'rolagens': data}, safe=False)


@login_required
def limpar_log(request):
    Rolagem.objects.all().delete()
    cache.delete('painel_estatisticas_data')
    return JsonResponse({'status': 'sucesso'})


# --- CRUD MESA ---

@login_required
def lista_mesas(request):
    mesas = Mesa.objects.all().order_by('-data_criacao')
    return render(request, 'lobby/lista_mesas.html', {'mesas': mesas})


@login_required
def criar_mesa(request):
    if request.method == "POST":
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa = form.save(commit=False)
            mesa.mestre = request.user
            mesa.save()
            messages.success(request, f"A mesa '{mesa.titulo}' foi erguida com sucesso!")
            return redirect('lista_mesas')
    else:
        form = MesaForm()
    return render(request, 'lobby/form_mesa.html', {'form': form})


# --- CRUD PERSONAGEM ---

@login_required
def lista_personagens(request):
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)

    busca_nome = request.GET.get('nome', '').strip()
    busca_classe = request.GET.get('classe', '').strip()
    busca_mesa = request.GET.get('mesa', '').strip()

    if busca_nome:
        personagens = personagens.filter(nome__icontains=busca_nome)
    if busca_classe:
        personagens = personagens.filter(classe__iexact=busca_classe)
    if busca_mesa:
        if busca_mesa == 'sem_mesa':
            personagens = personagens.filter(mesa__isnull=True)
        else:
            personagens = personagens.filter(mesa_id=busca_mesa)

    mesas_disponiveis = Mesa.objects.all().order_by('titulo')
    classes_disponiveis = ['Guerreiro', 'Mago', 'Ladino', 'Clérigo', 'Arqueiro', 'Bárbaro', 'Paladino']

    return render(request, 'lobby/lista_personagens.html', {
        'personagens': personagens.order_by('nome'),
        'mesas_disponiveis': mesas_disponiveis,
        'classes_disponiveis': classes_disponiveis,
        'filtros': {
            'nome': busca_nome,
            'classe': busca_classe,
            'mesa': busca_mesa
        }
    })


@login_required
def criar_personagem(request):
    if request.method == "POST":
        form = PersonagemForm(request.POST)
        if form.is_valid():
            personagem = form.save(commit=False)
            personagem.usuario = request.user
            personagem.save()
            messages.success(request, f"O herói {personagem.nome} entrou no lobby!")
            return redirect('lista_personagens')
    else:
        form = PersonagemForm()
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Criar Novo Personagem'})


@login_required
def editar_personagem(request, pk):
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)
    if request.method == "POST":
        form = PersonagemForm(request.POST, instance=personagem)
        if form.is_valid():
            form.save()
            messages.success(request, f"A ficha de {personagem.nome} foi atualizada!")
            return redirect('lista_personagens')
    else:
        form = PersonagemForm(instance=personagem)
    return render(request, 'lobby/form_personagem.html', {'form': form})


@login_required
def excluir_personagem(request, pk):
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)
    if request.method == "POST":
        personagem.ativo = False
        personagem.save()
        messages.warning(request, f"O personagem {personagem.nome} foi arquivado nas crônicas da taverna.")
        return redirect('lista_personagens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': personagem})


# --- CRUD ITENS ---

@login_required
def lista_itens(request):
    itens = Item.objects.filter(ativo=True).order_by('nome')
    return render(request, 'lobby/lista_itens.html', {'itens': itens})


@login_required
def criar_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Novo item adicionado com sucesso ao compêndio global!")
            return redirect('lista_itens')
    else:
        form = ItemForm()
    return render(request, 'lobby/form_item.html', {'form': form})


# --- INVENTÁRIO ---

@login_required
def gerenciar_inventario(request, pk):
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)

    if request.method == "POST":
        item_id = request.POST.get('item_id')
        if item_id:
            item = get_object_or_404(Item, pk=item_id, ativo=True)
            personagem.itens.add(item)
            messages.success(request, f"O item '{item.nome}' foi adicionado ao inventário de {personagem.nome}!")
            return redirect('gerenciar_inventario', pk=personagem.id)

    itens_disponiveis = Item.objects.filter(ativo=True).exclude(id__in=personagem.itens.all())
    return render(request, 'lobby/inventario.html', {
        'personagem': personagem,
        'itens_disponiveis': itens_disponiveis
    })


# --- AUTENTICAÇÃO ---

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'lobby/login.html', {'form': form})


def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Seja bem-vindo à taverna, {user.username}! Prepare os seus dados.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'lobby/registro.html', {'form': form})


# --- FICHA DO PERSONAGEM ---

@login_required
def ficha_personagem(request, pk):
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)
    modificadores = personagem.get_modificadores()
    proficiencia = 2 + (personagem.nivel - 1) // 4
    
    context = {
        'p': personagem,
        'mod': modificadores,
        'proficiencia': proficiencia,
        'pv_percent': (personagem.vida_atual / personagem.vida_maxima * 100) if personagem.vida_maxima > 0 else 0,
    }
    return render(request, 'lobby/ficha_personagem.html', context)


@login_required
def api_curar_personagem(request, pk):
    if request.method == "POST":
        personagem = get_object_or_404(Personagem, pk=pk)
        quantidade = int(request.POST.get('quantidade', 0))
        curado = personagem.curar(quantidade)
        return JsonResponse({
            'status': 'sucesso',
            'curado': curado,
            'vida_atual': personagem.vida_atual,
            'vida_maxima': personagem.vida_maxima
        })
    return JsonResponse({'status': 'erro'}, status=400)


@login_required
def api_dano_personagem(request, pk):
    if request.method == "POST":
        personagem = get_object_or_404(Personagem, pk=pk)
        quantidade = int(request.POST.get('quantidade', 0))
        resultado = personagem.tomar_dano(quantidade)
        return JsonResponse({
            'status': 'sucesso',
            'dano': resultado['dano'],
            'morreu': resultado['morreu'],
            'vida_atual': resultado['vida_restante']
        })
    return JsonResponse({'status': 'erro'}, status=400)


# ========== SISTEMA DE COMBATE ==========

@login_required
def iniciar_combate(request, mesa_id):
    """Inicia um novo combate em uma mesa"""
    mesa = get_object_or_404(Mesa, id=mesa_id, mestre=request.user)
    
    if request.method == "POST":
        nome = request.POST.get('nome', '⚔️ Combate')
        combate = Combate.objects.create(
            mesa=mesa,
            nome=nome,
            status='em_andamento'
        )
        
        # Adiciona todos os personagens da mesa como participantes
        personagens = Personagem.objects.filter(mesa=mesa, ativo=True)
        ordem = 0
        for p in personagens:
            # Rola iniciativa automaticamente (1d20 + modificador de destreza)
            iniciativa = random.randint(1, 20) + p.calcular_modificador(p.destreza)
            ParticipanteCombate.objects.create(
                combate=combate,
                personagem=p,
                nome=p.nome,
                tipo='heroi',
                iniciativa=iniciativa,
                ordem=ordem,
                vida_atual=p.vida_atual,
                vida_maxima=p.vida_maxima,
                defesa=10 + p.calcular_modificador(p.destreza)
            )
            ordem += 1
        
        # Ordena por iniciativa (maior primeiro)
        participantes = combate.participantes.all().order_by('-iniciativa')
        for i, p in enumerate(participantes):
            p.ordem = i
            p.save()
        
        messages.success(request, f"⚔️ Combate '{combate.nome}' iniciado com {participantes.count()} participantes!")
        return redirect('sala_combate', combate_id=combate.id)
    
    return render(request, 'lobby/combate/iniciar.html', {'mesa': mesa})


@login_required
def sala_combate(request, combate_id):
    """Sala de combate em tempo real"""
    combate = get_object_or_404(Combate, id=combate_id)
    participantes = combate.participantes.all().order_by('ordem')
    turno_atual = None
    
    if combate.status == 'em_andamento':
        participantes_vivos = participantes.filter(vivo=True)
        if participantes_vivos.exists():
            turno_atual = participantes_vivos[combate.turno_atual % participantes_vivos.count()]
    
    # Pega as últimas 10 ações para exibir
    acoes = combate.acoes.all().order_by('-data_hora')[:10]
    
    # Verifica se o usuário é o mestre da mesa
    eh_mestre = request.user == combate.mesa.mestre
    
    # Adiciona a classe CSS da barra de progresso para cada participante
    for p in participantes:
        if p.vida_maxima > 0:
            ratio = p.vida_atual / p.vida_maxima
            if ratio > 0.5:
                p.bar_class = 'bg-success'
            elif ratio > 0.25:
                p.bar_class = 'bg-warning'
            else:
                p.bar_class = 'bg-danger'
        else:
            p.bar_class = 'bg-danger'
    
    context = {
        'combate': combate,
        'participantes': participantes,
        'turno_atual': turno_atual,
        'eh_mestre': eh_mestre,
        'acoes': acoes,
    }
    return render(request, 'lobby/combate/sala_combate.html', context)


@login_required
def acao_combate(request, combate_id):
    """Registra uma ação no combate"""
    if request.method != "POST":
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    combate = get_object_or_404(Combate, id=combate_id)
    participante_id = request.POST.get('participante_id')
    acao = request.POST.get('acao')
    alvo_id = request.POST.get('alvo_id')
    descricao = request.POST.get('descricao', '')
    
    participante = get_object_or_404(ParticipanteCombate, id=participante_id, combate=combate)
    
    # Verifica se é o turno do participante
    participantes_vivos = combate.participantes.filter(vivo=True).order_by('ordem')
    if not participantes_vivos.exists():
        return JsonResponse({'erro': 'Todos os participantes estão mortos!'}, status=400)
    
    if participantes_vivos[combate.turno_atual % participantes_vivos.count()] != participante:
        return JsonResponse({'erro': 'Não é o seu turno!'}, status=400)
    
    resultado = ""
    alvo_nome = ""
    
    if acao == 'ataque':
        if alvo_id:
            alvo = get_object_or_404(ParticipanteCombate, id=alvo_id, combate=combate)
            alvo_nome = alvo.nome
            roll = random.randint(1, 20)
            if participante.tipo == 'heroi' and participante.personagem:
                modificador = participante.personagem.calcular_modificador(participante.personagem.forca)
            else:
                modificador = 2
            
            total_ataque = roll + modificador
            
            if total_ataque >= alvo.defesa:
                if participante.tipo == 'heroi' and participante.personagem:
                    dano_base = random.randint(1, 8) + modificador
                else:
                    dano_base = random.randint(1, 6) + 2
                
                resultado_dano = alvo.aplicar_dano(dano_base)
                resultado = f"🎯 {participante.nome} atacou {alvo.nome} com {total_ataque} de acerto! Dano: {dano_base}!"
                if not alvo.vivo:
                    resultado += f" 💀 {alvo.nome} foi derrotado!"
            else:
                resultado = f"❌ {participante.nome} errou o ataque contra {alvo.nome} (Total: {total_ataque} vs Defesa: {alvo.defesa})"
        else:
            resultado = f"⚠️ Nenhum alvo selecionado para o ataque!"
    
    elif acao == 'cura':
        if alvo_id:
            alvo = get_object_or_404(ParticipanteCombate, id=alvo_id, combate=combate)
            alvo_nome = alvo.nome
            quantidade = random.randint(4, 12)
            if participante.tipo == 'heroi' and participante.personagem:
                quantidade += participante.personagem.calcular_modificador(participante.personagem.sabedoria)
            resultado_cura = alvo.curar(quantidade)
            resultado = f"💚 {participante.nome} curou {alvo.nome} em {resultado_cura['curado']} pontos de vida!"
        else:
            resultado = f"⚠️ Nenhum alvo selecionado para cura!"
    
    elif acao == 'defesa':
        participante.defesa += 2
        participante.save()
        resultado = f"🛡️ {participante.nome} se preparou para defender! Defesa +2"
    
    else:
        resultado = f"⚠️ Ação '{acao}' não reconhecida!"
    
    # Registra a ação
    AcaoCombate.objects.create(
        participante=participante,
        combate=combate,
        rodada=combate.rodada,
        turno=combate.turno_atual,
        tipo=acao,
        descricao=descricao or f"{participante.nome} realizou {acao}",
        alvo=alvo_nome,
        resultado=resultado
    )
    
    # Avança para o próximo turno
    combate.proximo_turno()
    
    return JsonResponse({
        'sucesso': True,
        'resultado': resultado,
        'turno_atual': combate.turno_atual,
        'rodada': combate.rodada,
        'participantes': [
            {
                'id': p.id,
                'nome': p.nome,
                'vida': p.vida_atual,
                'vida_maxima': p.vida_maxima,
                'vivo': p.vivo,
                'defesa': p.defesa,
                'condicao': p.condicao
            }
            for p in combate.participantes.all()
        ]
    })


@login_required
def adicionar_monstro(request, combate_id):
    """Adiciona um monstro ao combate (apenas mestre)"""
    if request.method != "POST":
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    combate = get_object_or_404(Combate, id=combate_id)
    if request.user != combate.mesa.mestre:
        return JsonResponse({'erro': 'Apenas o mestre pode adicionar monstros!'}, status=403)
    
    nome = request.POST.get('nome')
    vida = int(request.POST.get('vida', 20))
    defesa = int(request.POST.get('defesa', 12))
    
    if not nome:
        return JsonResponse({'erro': 'Nome do monstro é obrigatório!'}, status=400)
    
    iniciativa = random.randint(1, 20) + random.randint(1, 4)
    ordem = combate.participantes.count()
    
    monstro = ParticipanteCombate.objects.create(
        combate=combate,
        nome=nome,
        tipo='monstro',
        iniciativa=iniciativa,
        ordem=ordem,
        vida_atual=vida,
        vida_maxima=vida,
        defesa=defesa
    )
    
    return JsonResponse({
        'sucesso': True,
        'monstro': {
            'id': monstro.id,
            'nome': monstro.nome,
            'vida': monstro.vida_atual,
            'vida_maxima': monstro.vida_maxima,
            'defesa': monstro.defesa
        }
    })


@login_required
def status_combate(request, combate_id):
    """Retorna o status atual do combate (para auto-refresh)"""
    combate = get_object_or_404(Combate, id=combate_id)
    return JsonResponse({
        'status': combate.status,
        'rodada': combate.rodada,
        'turno_atual': combate.turno_atual,
        'participantes': [
            {
                'id': p.id,
                'nome': p.nome,
                'vida': p.vida_atual,
                'vida_maxima': p.vida_maxima,
                'vivo': p.vivo,
                'defesa': p.defesa,
                'condicao': p.condicao
            }
            for p in combate.participantes.all()
        ]
    })


# ========== CHAT EM TEMPO REAL ==========

@login_required
def chat_mesa(request, mesa_id):
    """Página do chat da mesa"""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    # Verifica se o usuário pertence à mesa
    if request.user != mesa.mestre and not Personagem.objects.filter(usuario=request.user, mesa=mesa, ativo=True).exists():
        messages.error(request, "Você não tem acesso a esta mesa!")
        return redirect('lista_mesas')
    
    return render(request, 'lobby/chat.html', {'mesa': mesa})

# ========== SISTEMA DE MISSÕES ==========

@login_required
def lista_missoes(request, mesa_id):
    """Lista todas as missões de uma mesa"""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    # Verifica permissão
    if request.user != mesa.mestre and not Personagem.objects.filter(usuario=request.user, mesa=mesa, ativo=True).exists():
        messages.error(request, "Você não tem acesso a esta mesa!")
        return redirect('lista_mesas')
    
    missoes = Missao.objects.filter(mesa=mesa).order_by('-data_criacao')
    eh_mestre = request.user == mesa.mestre
    
    # Para cada missão, verifica o progresso do personagem logado
    personagem = Personagem.objects.filter(usuario=request.user, mesa=mesa, ativo=True).first()
    progressos = {}
    if personagem:
        for missao in missoes:
            try:
                progresso = MissaoPersonagem.objects.get(missao=missao, personagem=personagem)
                progressos[missao.id] = progresso
            except MissaoPersonagem.DoesNotExist:
                pass
    
    context = {
        'mesa': mesa,
        'missoes': missoes,
        'eh_mestre': eh_mestre,
        'personagem': personagem,
        'progressos': progressos,
    }
    return render(request, 'lobby/missoes/lista_missoes.html', context)


@login_required
def criar_missao(request, mesa_id):
    """Cria uma nova missão (apenas mestre)"""
    mesa = get_object_or_404(Mesa, id=mesa_id, mestre=request.user)
    
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        objetivos = request.POST.get('objetivos')
        recompensa_xp = int(request.POST.get('recompensa_xp', 0))
        recompensa_ouro = int(request.POST.get('recompensa_ouro', 0))
        dificuldade = request.POST.get('dificuldade', 'medio')
        prazo = request.POST.get('prazo')
        
        if not titulo or not descricao:
            messages.error(request, "Título e descrição são obrigatórios!")
            return redirect('criar_missao', mesa_id=mesa_id)
        
        missao = Missao.objects.create(
            mesa=mesa,
            titulo=titulo,
            descricao=descricao,
            objetivos=objetivos or descricao,
            recompensa_xp=recompensa_xp,
            recompensa_ouro=recompensa_ouro,
            dificuldade=dificuldade,
            criado_por=request.user,
            prazo=prazo if prazo else None
        )
        
        messages.success(request, f"📋 Missão '{missao.titulo}' criada com sucesso!")
        return redirect('lista_missoes', mesa_id=mesa_id)
    
    return render(request, 'lobby/missoes/criar_missao.html', {'mesa': mesa})


@login_required
def detalhes_missao(request, missao_id):
    """Detalhes de uma missão específica"""
    missao = get_object_or_404(Missao, id=missao_id)
    mesa = missao.mesa
    
    # Verifica permissão
    if request.user != mesa.mestre and not Personagem.objects.filter(usuario=request.user, mesa=mesa, ativo=True).exists():
        messages.error(request, "Você não tem acesso a esta missão!")
        return redirect('lista_mesas')
    
    # Progresso do personagem logado
    personagem = Personagem.objects.filter(usuario=request.user, mesa=mesa, ativo=True).first()
    progresso_personagem = None
    if personagem:
        try:
            progresso_personagem = MissaoPersonagem.objects.get(missao=missao, personagem=personagem)
        except MissaoPersonagem.DoesNotExist:
            pass
    
    # Todos os progressos (apenas para mestre)
    todos_progressos = None
    if request.user == mesa.mestre:
        todos_progressos = MissaoPersonagem.objects.filter(missao=missao).select_related('personagem')
    
    context = {
        'missao': missao,
        'mesa': mesa,
        'personagem': personagem,
        'progresso_personagem': progresso_personagem,
        'todos_progressos': todos_progressos,
        'eh_mestre': request.user == mesa.mestre,
    }
    return render(request, 'lobby/missoes/detalhes_missao.html', context)


@login_required
def atualizar_progresso_missao(request, missao_id):
    """Atualiza o progresso de uma missão (apenas mestre)"""
    if request.method != "POST":
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    missao = get_object_or_404(Missao, id=missao_id)
    if request.user != missao.mesa.mestre:
        return JsonResponse({'erro': 'Apenas o mestre pode atualizar progressos!'}, status=403)
    
    personagem_id = request.POST.get('personagem_id')
    novo_progresso = int(request.POST.get('progresso', 0))
    
    personagem = get_object_or_404(Personagem, id=personagem_id, mesa=missao.mesa)
    
    progresso_obj, created = MissaoPersonagem.objects.get_or_create(
        missao=missao,
        personagem=personagem
    )
    
    progresso_obj.atualizar_progresso(novo_progresso)
    
    return JsonResponse({
        'sucesso': True,
        'progresso': progresso_obj.progresso,
        'concluida': progresso_obj.concluida,
        'personagem': personagem.nome
    })


@login_required
def concluir_missao(request, missao_id):
    """Conclui uma missão (apenas mestre)"""
    missao = get_object_or_404(Missao, id=missao_id)
    if request.user != missao.mesa.mestre:
        messages.error(request, "Apenas o mestre pode concluir missões!")
        return redirect('detalhes_missao', missao_id=missao_id)
    
    if missao.status == 'concluida':
        messages.warning(request, "Esta missão já foi concluída!")
        return redirect('detalhes_missao', missao_id=missao_id)
    
    resultado = missao.concluir()
    messages.success(request, f"🏆 Missão '{missao.titulo}' concluída! {resultado['xp_distribuido']} XP distribuído para {resultado['personagens_afetados']} personagens!")
    
    return redirect('lista_missoes', mesa_id=missao.mesa.id)

# ========== SISTEMA DE NOTIFICAÇÕES ==========

from .notificacoes import criar_notificacao, notificacoes_nao_lidas

@login_required
def lista_notificacoes(request):
    """Lista todas as notificações do usuário"""
    notificacoes = Notificacao.objects.filter(usuario=request.user)
    nao_lidas = notificacoes.filter(lida=False)
    
    # Marcar como lidas
    for n in notificacoes:
        n.marcar_como_lida()
    
    context = {
        'notificacoes': notificacoes,
        'nao_lidas_count': nao_lidas.count(),
    }
    return render(request, 'lobby/notificacoes.html', context)


@login_required
def api_notificacoes_nao_lidas(request):
    """API para verificar notificações não lidas"""
    count = notificacoes_nao_lidas(request.user)
    return JsonResponse({
        'count': count,
        'has_unread': count > 0
    })


@login_required
def api_marcar_todas_lidas(request):
    """Marca todas as notificações como lidas"""
    if request.method == "POST":
        Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
        return JsonResponse({'sucesso': True})
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

# ========== DASHBOARD DO MESTRE ==========

@login_required
def dashboard_mestre(request, mesa_id):
    """Painel de controle do mestre para uma mesa"""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    if request.user != mesa.mestre:
        messages.error(request, "Apenas o mestre da mesa pode acessar este painel!")
        return redirect('lista_mesas')
    
    personagens = Personagem.objects.filter(mesa=mesa, ativo=True)
    
    # Adiciona a classe CSS da barra de progresso para cada personagem
    for p in personagens:
        if p.vida_maxima > 0:
            ratio = p.vida_atual / p.vida_maxima
            if ratio > 0.5:
                p.bar_class = 'bg-success'
            elif ratio > 0.25:
                p.bar_class = 'bg-warning'
            else:
                p.bar_class = 'bg-danger'
        else:
            p.bar_class = 'bg-danger'
    
    total_personagens = personagens.count()
    total_rolagens = Rolagem.objects.filter(mesa=mesa).count()
    total_missoes = Missao.objects.filter(mesa=mesa).count()
    missoes_concluidas = Missao.objects.filter(mesa=mesa, status='concluida').count()
    
    ultimas_rolagens = Rolagem.objects.filter(mesa=mesa).order_by('-data_hora')[:10]
    ultimas_missoes = Missao.objects.filter(mesa=mesa).order_by('-data_criacao')[:5]
    
    combate_ativo = Combate.objects.filter(mesa=mesa, status='em_andamento').first()
    personagens_feridos = personagens.filter(vida_atual__lt=10)
    
    context = {
        'mesa': mesa,
        'personagens': personagens,  # Já tem a bar_class adicionada
        'total_personagens': total_personagens,
        'total_rolagens': total_rolagens,
        'total_missoes': total_missoes,
        'missoes_concluidas': missoes_concluidas,
        'ultimas_rolagens': ultimas_rolagens,
        'ultimas_missoes': ultimas_missoes,
        'combate_ativo': combate_ativo,
        'personagens_feridos': personagens_feridos,
    }
    return render(request, 'lobby/mestre/dashboard_mestre.html', context)


@login_required
def api_mestre_curar_personagem(request, mesa_id, personagem_id):
    """API para curar um personagem (mestre)"""
    if request.method != "POST":
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    mesa = get_object_or_404(Mesa, id=mesa_id)
    if request.user != mesa.mestre:
        return JsonResponse({'erro': 'Apenas o mestre pode curar personagens!'}, status=403)
    
    personagem = get_object_or_404(Personagem, id=personagem_id, mesa=mesa)
    quantidade = int(request.POST.get('quantidade', 10))
    
    curado = personagem.curar(quantidade)
    
    return JsonResponse({
        'sucesso': True,
        'personagem': personagem.nome,
        'vida_atual': personagem.vida_atual,
        'vida_maxima': personagem.vida_maxima,
        'curado': curado
    })


@login_required
def api_mestre_status_personagens(request, mesa_id):
    """API para obter status de todos os personagens da mesa"""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    if request.user != mesa.mestre:
        return JsonResponse({'erro': 'Apenas o mestre pode acessar esta informação!'}, status=403)
    
    personagens = Personagem.objects.filter(mesa=mesa, ativo=True)
    data = []
    for p in personagens:
        data.append({
            'id': p.id,
            'nome': p.nome,
            'vida_atual': p.vida_atual,
            'vida_maxima': p.vida_maxima,
            'vida_percent': round(p.vida_atual / p.vida_maxima * 100, 1) if p.vida_maxima > 0 else 0,
            'nivel': p.nivel,
            'classe': p.classe,
            'raca': p.raca,
            'itens': p.itens.count(),
        })
    
    return JsonResponse({'personagens': data})