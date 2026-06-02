import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Max
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.core.cache import cache  # --- REQUISITO (viii): Módulo de Gerenciamento de Cache ---
from .models import Rolagem, Personagem, Mesa, Item
from .forms import PersonagemForm, MesaForm, ItemForm


# --- REQUISITO: PAINEL DE ESTATÍSTICAS (Aggregation + Cache de Baixo Nível) ---

@login_required
def painel_estatisticas(request):
    """Gera inteligência de dados processada com estratégia de cache em banco."""
    # 1. Tenta recuperar os cálculos prontos da tabela de cache do PostgreSQL
    stats = cache.get('painel_estatisticas_data')
    
    # 2. Se o cache expirou ou não existir, faz o processamento pesado e salva no cache
    if not stats:
        stats = {
            'total_rolagens': Rolagem.objects.count(),
            'media_geral': Rolagem.objects.aggregate(Avg('resultado'))['resultado__avg'] or 0,
            'maior_valor': Rolagem.objects.aggregate(Max('resultado'))['resultado__max'] or 0,
            'rank_jogadores': Rolagem.objects.values('jogador_nome').annotate(total=Count('id')).order_by('-total')[:5]
        }
        # Guarda no cache por 5 minutos (300 segundos)
        cache.set('painel_estatisticas_data', stats, 300)
        
    return render(request, 'lobby/estatisticas.html', {'stats': stats})


# --- REQUISITO: SISTEMA DE ROLLBACK (Segurança e Controle de Versão) ---

@login_required
def rollback_rolagem(request, pk):
    """Permite ao mestre reverter/editar o valor de um dado lançado incorretamente."""
    rolagem = get_object_or_404(Rolagem, pk=pk)

    # REQUISITO DE SEGURANÇA: Apenas o mestre daquela mesa pode realizar auditoria e alteração
    if rolagem.mesa and rolagem.mesa.mestre != request.user:
        return HttpResponseForbidden("Apenas o Mestre desta mesa tem permissão para alterar os dados da história.")

    if request.method == "POST":
        novo_resultado = request.POST.get('novo_resultado')
        motivo = request.POST.get('motivo')

        if novo_resultado:
            # Preserva o histórico antes de aplicar a alteração (Auditoria de Dados)
            rolagem.resultado_anterior = rolagem.resultado
            rolagem.resultado = int(novo_resultado)
            rolagem.editado = True
            rolagem.motivo_edicao = motivo
            rolagem.save()
            
            # Limpa o cache das estatísticas para que o painel se atualize no próximo acesso
            cache.delete('painel_estatisticas_data')
            
            messages.success(request, f"O dado de {rolagem.jogador_nome} foi alterado com sucesso para {novo_resultado}!")
            return redirect('dashboard')

    return render(request, 'lobby/rollback.html', {'rolagem': rolagem})


# --- REQUISITO: SISTEMA DE ROLAGEM DE DADOS (API REST + AJAX) ---

@csrf_exempt
def salvar_rolagem(request):
    """API Endpoint para registrar rolagens enviadas assincronamente pelo JavaScript via AJAX."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            personagem_id = data.get('personagem_id')
            
            personagem = None
            if personagem_id:
                # Filtrado para aceitar apenas personagens que não sofreram Soft Delete
                personagem = Personagem.objects.filter(id=personagem_id, ativo=True).first()

            # Define a mesa baseada no personagem, se ele existir
            mesa = personagem.mesa if personagem else None

            rolagem = Rolagem.objects.create(
                personagem=personagem,
                mesa=mesa,
                jogador_nome=data.get('jogador_nome', 'Aventureiro Anônimo'),
                tipo_dado=data.get('tipo_dado', 'D20'),
                resultado=int(data.get('resultado', 1))
            )
            
            # Limpa o cache do painel para manter dados em tempo real após uma jogada
            cache.delete('painel_estatisticas_data')

            return JsonResponse({
                'status': 'success',
                'id': rolagem.id,
                'jogador': rolagem.jogador_nome,
                'resultado': rolagem.resultado
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Método inválido'}, status=405)


def listar_rolagens(request):
    """Retorna o histórico de rolagens em formato JSON para atualização dinâmica da tela."""
    rolagens = Rolagem.objects.all().order_by('-data_hora')[:20]
    data = []
    for r in rolagens:
        data_formatada = timezone.localtime(r.data_hora).strftime('%d/%m/%y %H:%M:%S')
        data.append({
            'id': r.id,
            'jogador': r.personagem.nome if r.personagem else r.jogador_nome,
            'dado': r.tipo_dado,
            'resultado': r.resultado,
            'data_hora': data_formatada,
            'editado': r.editado,
            'resultado_anterior': r.resultado_anterior,
            'motivo_edicao': r.motivo_edicao,
            'mesa_mestre_id': r.mesa.mestre.id if r.mesa else None
        })
    return JsonResponse({'rolagens': data})


@csrf_exempt
def limpar_log(request):
    """Limpa o histórico de jogadas do banco de dados."""
    if request.method == 'POST':
        Rolagem.objects.all().delete()
        cache.delete('painel_estatisticas_data')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# --- VIEWS TRADICIONAIS: DASHBOARD PRINCIPAL ---

@login_required
def dashboard(request):
    """Renderiza a central de controle do RPG filtrando apenas entidades ativas (Soft Delete)."""
    # Exibe apenas as mesas ativas
    mesas = Mesa.objects.filter(ativo=True).select_related('mestre')
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    return render(request, 'lobby/dashboard.html', {'mesas': mesas, 'personagens': personajes})


# --- CRUD COMPLETO DA ENTIDADE 1: MESA (Com Soft Delete) ---

@login_required
def lista_mesas(request):
    """Lista todas as salas de campanha ativas na taverna."""
    mesas = Mesa.objects.filter(ativo=True).select_related('mestre')
    return render(request, 'lobby/lista_mesas.html', {'mesas': mesas})


@login_required
def criar_mesa(request):
    """Abre uma nova sala de campanha na taverna."""
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa = form.save(commit=False)
            mesa.mestre = request.user
            mesa.save()
            messages.success(request, f"Mesa '{mesa.titulo}' erguida com sucesso!")
            return redirect('lista_mesas')
    else:
        form = MesaForm()
    return render(request, 'lobby/form_mesa.html', {'form': form})


@login_required
def editar_mesa(request, pk):
    """Permite ao mestre ajustar as configurações ou descrição da mesa."""
    mesa = get_object_or_404(Mesa, pk=pk, mestre=request.user, ativo=True)
    if request.method == 'POST':
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            messages.success(request, f"Mesa '{mesa.titulo}' atualizada com sucesso!")
            return redirect('lista_mesas')
    else:
        form = MesaForm(instance=mesa)
    return render(request, 'lobby/form_mesa.html', {'form': form})


@login_required
def excluir_mesa(request, pk):
    """Executa a desativação lógica (Soft Delete) da mesa protegida por segurança."""
    mesa = get_object_or_404(Mesa, pk=pk, mestre=request.user, ativo=True)
    if request.method == 'POST':
        mesa.ativo = False  # Soft Delete aplicado à Mesa
        mesa.save()
        messages.warning(request, f"A mesa '{mesa.titulo}' foi arquivada permanentemente.")
        return redirect('lista_mesas')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': mesa})


# --- CRUD COMPLETO DA ENTIDADE 2: PERSONAGEM (Com Soft Delete) ---

@login_required
def lista_personagens(request):
    """Exibe a lista de heróis ativos pertencentes ao usuário logado."""
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    return render(request, 'lobby/lista_personagens.html', {'personagens': personagens})


@login_required
def criar_personagem(request):
    """Forja a ficha de um novo herói e vincula ao usuário."""
    if request.method == 'POST':
        form = PersonagemForm(request.POST)
        if form.is_valid():
            personagem = form.save(commit=False)
            personagem.usuario = request.user
            personagem.save()
            messages.success(request, f"Ficha de {personagem.nome} criada! Que a sorte guie seus passos.")
            return redirect('lista_personagens')
    else:
        form = PersonagemForm()
    return render(request, 'lobby/form_personagem.html', {'form': form})


@login_required
def editar_personagem(request, pk):
    """Permite ajustar atributos, nível ou vida da ficha do personagem."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)
    if request.method == 'POST':
        form = PersonagemForm(request.POST, instance=personagem)
        if form.is_valid():
            form.save()
            messages.success(request, f"Atributos de {personagem.nome} atualizados com sucesso!")
            return redirect('lista_personagens')
    else:
        form = PersonagemForm(instance=personagem)
    return render(request, 'lobby/form_personagem.html', {'form': form})


@login_required
def excluir_personagem(request, pk):
    """Executa a desativação lógica (Soft Delete) do personagem para segurança dos dados."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)
    if request.method == 'POST':
        personagem.ativo = False  # Soft Delete aplicado ao Personagem
        personagem.save()
        messages.warning(request, f"{personagem.nome} retirou-se da taverna de forma permanente.")
        return redirect('lista_personagens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': personagem})


# --- CRUD COMPLETO DA ENTIDADE 3: ITEM / ARTEFATO (Com Soft Delete) ---

@login_required
def lista_itens(request):
    """Abre o catálogo global de itens e artefatos ativos cadastrados na taverna."""
    itens = Item.objects.filter(ativo=True)
    return render(request, 'lobby/lista_itens.html', {'itens': itens})


@login_required
def criar_item(request):
    """Forja um novo equipamento no acervo global do mundo."""
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Novo artefato registrado na forja global!")
            return redirect('lista_itens')
    else:
        form = ItemForm()
    return render(request, 'lobby/form_item.html', {'form': form})


@login_required
def editar_item(request, pk):
    """Permite alterar propriedades, peso ou raridade de um item existente."""
    item = get_object_or_404(Item, pk=pk, ativo=True)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"O item '{item.nome}' foi modificado com sucesso!")
            return redirect('lista_itens')
    else:
        form = ItemForm(instance=item)
    return render(request, 'lobby/form_item.html', {'form': form})


@login_required
def excluir_item(request, pk):
    """Executa Soft Delete no Item para removê-lo do catálogo sem quebrar inventários M2M."""
    item = get_object_or_404(Item, pk=pk, ativo=True)
    if request.method == 'POST':
        item.ativo = False  # Soft Delete aplicado ao Item
        item.save()
        messages.warning(request, f"O artefato '{item.nome}' foi descontinuado do acervo global.")
        return redirect('lista_itens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': item})


# --- NOVO REQUISITO: GESTÃO DE INVENTÁRIO (Many-to-Many) ---

@login_required
def gerenciar_inventario(request, pk):
    """Vincula ou desvincula itens no inventário Many-to-Many do Personagem."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)

    if request.method == "POST":
        item_id = request.POST.get('item_id')
        if item_id:
            item = get_object_or_404(Item, pk=item_id, ativo=True)
            personagem.itens.add(item)
            messages.success(request, f"O item '{item.nome}' foi adicionado ao inventário de {personagem.nome}!")
            return redirect('gerenciar_inventario', pk=personagem.id)

    # Lista apenas os itens ativos globais que o personagem ainda não possui
    itens_disponiveis = Item.objects.filter(ativo=True).exclude(id__in=personagem.itens.all())
    return render(request, 'lobby/inventario.html', {
        'personagem': personagem,
        'itens_disponiveis': itens_disponiveis
    })


# --- AUTENTICAÇÃO: Criação de Contas ---

def registro(request):
    """Permite que novos aventureiros criem uma conta na taverna."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bem-vindo à taverna, {user.username}! Sua conta foi criada.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registro.html', {'form': form})