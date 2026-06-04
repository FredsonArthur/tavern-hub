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
from django.core.cache import cache  # --- REQUISITO: Módulo de Gerenciamento de Cache ---
from .models import Rolagem, Personagem, Mesa, Item
from .forms import PersonagemForm, MesaForm, ItemForm


# --- REQUISITO: PAINEL DE ESTATÍSTICAS (Aggregation + Cache de Baixo Nível) ---

@login_required
def painel_estatisticas(request):
    """Gera inteligência de dados processada com estratégia de cache em banco."""
    # 1. Tenta recuperar os cálculos prontos da tabela de cache ativa (SQLite local ou Postgres remoto)
    stats = cache.get('painel_estatisticas_data')
    
    # 2. Se o cache expirou ou não existir, faz o processamento pesado e salva no cache
    if not stats:
        stats = {
            'total_rolagens': Rolagem.objects.count(),
            'media_geral': Rolagem.objects.aggregate(Avg('resultado'))['resultado__avg'] or 0,
            'maior_valor': Rolagem.objects.aggregate(Max('resultado'))['resultado__max'] or 0,
            'rank_jogadores': Rolagem.objects.values('jogador_nome')
                                            .annotate(total=Count('id'))
                                            .order_by('-total')[:5]
        }
        # Guarda no cache por 5 minutos (300 segundos)
        cache.set('painel_estatisticas_data', stats, 300)

    return render(request, 'lobby/estatisticas.html', {'stats': stats})


# --- LOBBY PRINCIPAL / DASHBOARD ---

@login_required
def dashboard(request):
    """Tela principal que lista as mesas ativas do usuário e permite interações."""
    mesas = Mesa.objects.all().order_by('-data_criacao')
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    return render(request, 'lobby/dashboard.html', {
        'mesas': mesas,
        'personagens': personagens
    })


# --- REQUISITO: SISTEMA DE ROLLBACK (Controle de Versão de Auditoria) ---

@login_required
def rollback_rolagem(request, pk):
    """
    Permite apenas ao MESTRE da mesa reverter ou auditar o resultado de um dado.
    Guarda o histórico da alteração para integridade dos dados.
    """
    rolagem = get_object_or_404(Rolagem, pk=pk)
    
    # Restrição de Segurança: Se a rolagem pertence a uma mesa, apenas o mestre dela edita
    if rolagem.mesa and rolagem.mesa.mestre != request.user:
        return HttpResponseForbidden("Apenas o Mestre desta mesa pode alterar o destino dos dados.")

    if request.method == "POST":
        novo_resultado = request.POST.get('novo_resultado')
        motivo = request.POST.get('motivo')

        if novo_resultado and motivo:
            # Salva o estado anterior (Auditoria / Rollback)
            rolagem.resultado_anterior = rolagem.resultado
            rolagem.resultado = int(novo_resultado)
            rolagem.editado = True
            rolagem.motivo_edicao = motivo
            rolagem.save()
            
            # Força a invalidação do cache de estatísticas para recalcular as médias
            cache.delete('painel_estatisticas_data')
            
            messages.success(request, "O tecido do destino foi alterado! Rolagem modificada com sucesso.")
            return redirect('dashboard')

    return render(request, 'lobby/rollback.html', {'rolagem': rolagem})


# --- ENDPOINTS DA API DE ROLAGENS (Integração assíncrona JS) ---

@csrf_exempt
@login_required
def salvar_rolagem(request):
    """Endpoint API para registrar rolagens de dados via chamadas assíncronas."""
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
                # CORRIGIDO: Se a API de teste não enviar a mesa explicitamente, herda a mesa vinculada ao herói
                mesa = personagem.mesa

            rolagem = Rolagem.objects.create(
                personagem=personagem,
                mesa=mesa,
                jogador_nome=personagem.nome if personagem else request.user.username,
                tipo_dado=data.get('tipo_dado', 'D20'),
                resultado=int(data.get('resultado'))
            )
            
            # Força a limpeza do cache de estatísticas a cada nova rolagem
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
    """Retorna o log de todas as rolagens ordenadas por tempo."""
    rolagens = Rolagem.objects.all().order_by('-data_hora')[:30]
    data = [{
        'id': r.id,
        'jogador': r.jogador_nome,
        'tipo_dado': r.tipo_dado,
        'resultado': r.resultado,
        'editado': r.editado,
        'resultado_anterior': r.resultado_anterior,
        'motivo': r.motivo_edicao,
        'data_hora': r.data_hora.strftime('%H:%M:%S')
    } for r in rolagens]
    return JsonResponse(data, safe=False)


@login_required
def limpar_log(request):
    """Limpa o histórico de rolagens do banco de dados."""
    Rolagem.objects.all().delete()
    cache.delete('painel_estatisticas_data')
    return JsonResponse({'status': 'sucesso'})


# --- CRUD: MESA (Entidade Protegida) ---

@login_required
def lista_mesas(request):
    """Lista todas as mesas registradas."""
    mesas = Mesa.objects.all().order_by('-data_criacao')
    return render(request, 'lobby/lista_mesas.html', {'mesas': mesas})


@login_required
def criar_mesa(request):
    """Cria uma nova mesa onde o usuário logado se torna automaticamente o Mestre."""
    if request.method == "POST":
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa = form.save(commit=False)
            mesa.mestre = request.user  # Vincula automaticamente o criador como mestre
            mesa.save()
            messages.success(request, f"A mesa '{mesa.titulo}' foi erguida com sucesso!")
            return redirect('lista_mesas')
    else:
        form = MesaForm()
    return render(request, 'lobby/form_mesa.html', {'form': form})


# --- CRUD: PERSONAGEM (Com suporte a Soft Delete) ---

@login_required
def lista_personagens(request):
    """Lista apenas heróis ativos do próprio utilizador logado."""
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    # CORRIGIDO: Retornando corretamente o contexto do dicionário 'personagens' sem erros de digitação
    return render(request, 'lobby/lista_personagens.html', {'personagens': personagens})


@login_required
def criar_personagem(request):
    """Registra uma nova ficha de personagem associando-a ao usuário atual."""
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
    return render(request, 'lobby/form_personagem.html', {'form': form})


@login_required
def editar_personagem(request, pk):
    """Edita a ficha de um personagem ativo do usuário."""
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
    """
    Executa a exclusão lógica (Soft Delete) exigida.
    Altera a flag 'ativo' para False em vez de expurgar o registro do banco de dados.
    """
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)
    if request.method == "POST":
        personagem.ativo = False
        personagem.save()
        messages.warning(request, f"O personagem {personagem.nome} foi arquivado nas crônicas da taverna.")
        return redirect('lista_personagens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': personagem})


# --- CRUD: ITENS & BIBLIOTECA GLOBAL ---

@login_required
def lista_itens(request):
    """Lista todos os itens cadastrados no catálogo global da taverna."""
    itens = Item.objects.filter(ativo=True).order_by('nome')
    return render(request, 'lobby/lista_itens.html', {'itens': itens})


@login_required
def criar_item(request):
    """Permite forjar um novo item na biblioteca global do cenário."""
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Novo item adicionado com sucesso ao compêndio global!")
            return redirect('lista_itens')
    else:
        form = ItemForm()
    return render(request, 'lobby/form_item.html', {'form': form})


# --- INVENTÁRIO (Relacionamento Many-to-Many) ---

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
            messages.success(request, f"Seja bem-vindo à taverna, {user.username}! Prepare os seus dados.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})