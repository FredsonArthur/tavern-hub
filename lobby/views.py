import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Max
from .models import Rolagem, Personagem, Mesa, Item
from .forms import PersonagemForm, MesaForm, ItemForm


# --- REQUISITO: PAINEL DE ESTATÍSTICAS (Aggregation) ---

@login_required
def painel_estatisticas(request):
    """Gera inteligência de dados processada diretamente no Banco de Dados."""
    stats = {
        'total_rolagens': Rolagem.objects.count(),
        'media_geral': Rolagem.objects.aggregate(Avg('resultado'))['resultado__avg'] or 0,
        'maior_valor': Rolagem.objects.aggregate(Max('resultado'))['resultado__max'] or 0,
        'rank_jogadores': Rolagem.objects.values('jogador_nome').annotate(total=Count('id')).order_by('-total')[:5]
    }
    return render(request, 'lobby/estatisticas.html', {'stats': stats})


# --- REQUISITO: SISTEMA DE ROLLBACK (Segurança e Controle de Versão) ---

@login_required
def rollback_rolagem(request, pk):
    """Permite corrigir um valor salvando a versão anterior para auditoria."""
    rolagem = get_object_or_404(Rolagem, pk=pk)

    # REGRA DE NEGÓCIO: Apenas o mestre da mesa vinculada à rolagem possui a permissão de alteração
    if rolagem.mesa and rolagem.mesa.mestre != request.user:
        return HttpResponseForbidden("Apenas o Mestre desta mesa pode realizar alterações de auditoria.")

    if request.method == 'POST':
        novo_valor = request.POST.get('novo_resultado')
        motivo = request.POST.get('motivo')

        if novo_valor:
            # Sincroniza o histórico antes de alterar
            rolagem.resultado_anterior = rolagem.resultado
            rolagem.resultado = int(novo_valor)
            rolagem.editado = True
            rolagem.motivo_edicao = motivo if motivo else "Correção Manual"
            rolagem.save()

            messages.success(request, f"Rolagem de {rolagem.jogador_nome} auditada com sucesso!")
            return redirect('dashboard')

    return render(request, 'lobby/form_rollback.html', {'rolagem': rolagem})


# --- Rotas Principais (Dashboard e APIs) ---

def dashboard(request):
    """Renderiza a mesa de jogo e o painel de rolagens dinâmicas."""
    # Filtra apenas os personagens ativos do usuário logado (se houver)
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True) if request.user.is_authenticated else None
    return render(request, 'lobby/index.html', {'personagens': personagens})


@csrf_exempt
def salvar_rolagem(request):
    """API endpoint para salvar as rolagens assíncronas calculadas no front-end."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            personagem_id = data.get('personagem_id')

            personagem = None
            mesa = None

            if personagem_id and personagem_id != "None":
                personagem = Personagem.objects.get(pk=personagem_id)
                mesa = personagem.mesa

            Rolagem.objects.create(
                personagem=personagem,
                mesa=mesa,
                jogador_nome=data.get('jogador', 'Aventureiro'),
                tipo_dado=data.get('tipo_dado', 'D20'),
                resultado=int(data.get('resultado'))
            )
            return JsonResponse({'status': 'sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'erro'}, status=405)


def listar_rolagens(request):
    """Lista as últimas 10 rolagens usando select_related para evitar queries N+1 ao buscar o Personagem."""
    tipo_filtro = request.GET.get('tipo')

    # OTIMIZAÇÃO: Traz os dados do Personagem no mesmo JOIN inicial
    rolagens = Rolagem.objects.all().select_related('personagem').order_by('-data_hora')

    if tipo_filtro:
        rolagens = rolagens.filter(tipo_dado=tipo_filtro)

    dados = []
    for r in rolagens[:10]:
        dados.append({
            "jogador": r.personagem.nome if r.personagem else r.jogador_nome,
            "tipo_dado": r.tipo_dado,
            "resultado": r.resultado,
            "data": timezone.localtime(r.data_hora).strftime('%H:%M:%S'),
            "editado": r.editado,
            "id": r.id
        })
    return JsonResponse({'rolagens': dados})


@login_required
def limpar_log(request):
    """Remove todo o histórico de rolagens (Apenas Staff/Admins)."""
    if request.user.is_staff:
        Rolagem.objects.all().delete()
        messages.error(request, "O log de rolagens foi limpo.")
        return JsonResponse({'status': 'sucesso'})
    return JsonResponse({'status': 'erro', 'message': 'Não autorizado'}, status=403)


# --- CRUD: Gestão de Mesas (Protegida) ---

@login_required
def lista_mesas(request):
    """Exibe as mesas gerenciadas pelo usuário logado."""
    mesas = Mesa.objects.filter(mestre=request.user)
    return render(request, 'lobby/lista_mesas.html', {'mesas': mesas})


@login_required
def criar_mesa(request):
    """Cria uma nova mesa de RPG associando o usuário logado como Mestre."""
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa = form.save(commit=False)
            mesa.mestre = request.user
            mesa.save()
            return redirect('lista_mesas')
    else:
        form = MesaForm()
    return render(request, 'lobby/form_mesa.html', {'form': form, 'titulo': 'Fundar Nova Mesa'})


# --- CRUD: Gestão de Personagens (Soft Delete ativo) ---

@login_required
def lista_personagens(request):
    """Exibe apenas heróis ativos (Soft Delete ativo)."""
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    return render(request, 'lobby/lista_personagens.html', {'personagens': personagens})


@login_required
def criar_personagem(request):
    """Instancia um novo herói na taverna."""
    if request.method == 'POST':
        form = PersonagemForm(request.POST)
        if form.is_valid():
            personagem = form.save(commit=False)
            personagem.usuario = request.user
            personagem.save()
            return redirect('lista_personagens')
    else:
        form = PersonagemForm()
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Criar Novo Herói'})


@login_required
def editar_personagem(request, pk):
    """Modifica os atributos de uma ficha existente."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)
    if request.method == 'POST':
        form = PersonagemForm(request.POST, instance=personagem)
        if form.is_valid():
            form.save()
            return redirect('lista_personagens')
    else:
        form = PersonagemForm(instance=personagem)
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': f'Editar {personagem.nome}'})


@login_required
def excluir_personagem(request, pk):
    """Executa a exclusão lógica (Soft Delete) do personagem."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)
    if request.method == 'POST':
        personagem.ativo = False
        personagem.save()
        return redirect('lista_personagens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': personagem})


# --- SISTEMA DE INVENTÁRIO (Many-to-Many) ---

@login_required
def lista_itens(request):
    """Exibe todos os itens registrados no banco global do arsenal."""
    itens = Item.objects.all()
    return render(request, 'lobby/lista_itens.html', {'itens': itens})


@login_required
def criar_item(request):
    """Forja um novo equipamento no arsenal da taverna."""
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_itens')
    else:
        form = ItemForm()
    return render(request, 'lobby/form_item.html', {'form': form})


@login_required
def gerenciar_inventario(request, pk):
    """Vincula ou desvincula itens no inventário Many-to-Many do Personagem."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user, ativo=True)

    if request.method == "POST":
        item_id = request.POST.get('item_id')
        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            personagem.itens.add(item)
            # Django Signals cuidará do alerta automático de itens raros!
            return redirect('gerenciar_inventario', pk=personagem.id)

    itens_disponiveis = Item.objects.exclude(id__in=personagem.itens.all())
    return render(request, 'lobby/inventario.html', {
        'personagem': personagem,
        'itens_disponiveis': itens_disponiveis
    })