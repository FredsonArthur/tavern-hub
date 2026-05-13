import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Max
from .models import Rolagem, Personagem, Mesa, Item
from .forms import PersonagemForm, MesaForm

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
    
    if rolagem.mesa and rolagem.mesa.mestre != request.user and not request.user.is_superuser:
        messages.error(request, "Apenas o mestre pode realizar correções nesta mesa.")
        return HttpResponseForbidden("Apenas o mestre pode realizar correções nesta mesa.")

    if request.method == 'POST':
        novo_valor = request.POST.get('novo_resultado')
        if novo_valor:
            rolagem.resultado_anterior = rolagem.resultado
            rolagem.resultado = int(novo_valor)
            rolagem.editado = True
            rolagem.motivo_edicao = request.POST.get('motivo', 'Correção de erro')
            rolagem.save()
            messages.success(request, f"Rolagem de {rolagem.jogador_nome} corrigida com sucesso!")
            return redirect('dashboard')
            
    return render(request, 'lobby/form_rollback.html', {'rolagem': rolagem})

# --- CRUD DE MESA (Protegida) ---

@login_required
def lista_mesas(request):
    mesas = Mesa.objects.filter(mestre=request.user)
    return render(request, 'lobby/lista_mesas.html', {'mesas': mesas})

@login_required
def criar_mesa(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa = form.save(commit=False)
            mesa.mestre = request.user 
            mesa.save()
            messages.success(request, f"Mesa '{mesa.titulo}' criada!")
            return redirect('lista_mesas')
    else:
        form = MesaForm()
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Criar Nova Mesa'})

# --- CRUD DE PERSONAGEM (Com Soft Delete) ---

@login_required
def lista_personagens(request):
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    return render(request, 'lobby/lista_personagens.html', {'personagens': personagens})

@login_required
def criar_personagem(request):
    if request.method == 'POST':
        form = PersonagemForm(request.POST)
        if form.is_valid():
            personagem = form.save(commit=False)
            personagem.usuario = request.user
            personagem.save()
            messages.success(request, f"O herói {personagem.nome} foi registrado!")
            return redirect('lista_personagens')
    else:
        form = PersonagemForm()
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Novo Personagem'})

@login_required
def editar_personagem(request, pk):
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = PersonagemForm(request.POST, instance=personagem)
        if form.is_valid():
            form.save()
            messages.info(request, f"Ficha de {personagem.nome} atualizada.")
            return redirect('lista_personagens')
    else:
        form = PersonagemForm(instance=personagem)
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Editar Personagem'})

@login_required
def excluir_personagem(request, pk):
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    if request.method == 'POST':
        personagem.ativo = False 
        personagem.save()
        messages.warning(request, f"{personagem.nome} foi arquivado.")
        return redirect('lista_personagens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': personageme})

# --- NOVO: GESTÃO DE INVENTÁRIO (Many-to-Many) ---

@login_required
def gerenciar_inventario(request, pk):
    """Lógica para adicionar itens ao inventário de um personagem específico."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    itens_disponiveis = Item.objects.all()

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Item, id=item_id)
        personagem.itens.add(item) # Relacionamento Many-to-Many
        messages.success(request, f"{item.nome} adicionado ao inventário de {personagem.nome}!")
        return redirect('gerenciar_inventario', pk=personagem.pk)

    return render(request, 'lobby/inventario.html', {
        'personagem': personagem,
        'itens': itens_disponiveis
    })

# --- LÓGICA DE ROLAGENS (API) ---

@csrf_exempt
def salvar_rolagem(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            personagem_id = data.get('personagem_id')
            personagem = Personagem.objects.filter(id=personagem_id, ativo=True).first() if personagem_id else None

            Rolagem.objects.create(
                personagem=personagem,
                mesa=personagem.mesa if personagem else None,
                jogador_nome=data.get('jogador', 'Aventureiro'),
                tipo_dado=data.get('tipo_dado', 'D20'),
                resultado=int(data.get('resultado'))
            )
            return JsonResponse({'status': 'sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'erro'}, status=405)

def listar_rolagens(request):
    tipo_filtro = request.GET.get('tipo')
    rolagens = Rolagem.objects.all().order_by('-data_hora')
    
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
    if request.user.is_staff: 
        Rolagem.objects.all().delete()
        messages.error(request, "O log de rolagens foi limpo.")
        return JsonResponse({'status': 'sucesso'})
    return JsonResponse({'status': 'erro'}, status=403)

def dashboard(request):
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True) if request.user.is_authenticated else []
    return render(request, 'lobby/index.html', {'personagens': personagens})