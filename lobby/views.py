import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Rolagem, Personagem, Mesa
from .forms import PersonagemForm, MesaForm

# --- VIEWS DE NAVEGAÇÃO ---

def dashboard(request):
    """Renderiza a página principal com foco em personagens ATIVOS."""
    personagens = []
    if request.user.is_authenticated:
        # PONTO 2: Filtro para mostrar apenas personagens que não sofreram Soft Delete[cite: 3]
        personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    return render(request, 'lobby/index.html', {'personagens': personagens})

# --- CRUD DE MESA (Entidade 1) ---

@login_required
def lista_mesas(request):
    """Lista as mesas onde o usuário logado é o mestre[cite: 4]."""
    mesas = Mesa.objects.filter(mestre=request.user)
    return render(request, 'lobby/lista_mesas.html', {'mesas': mesas})

@login_required
def criar_mesa(request):
    """Cria uma nova mesa vinculada ao mestre logado[cite: 4]."""
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa = form.save(commit=False)
            mesa.mestre = request.user
            mesa.save()
            return redirect('lista_mesas')
    else:
        form = MesaForm()
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Criar Nova Mesa'})

# --- CRUD DE PERSONAGEM (Entidade 2) ---

@login_required
def lista_personagens(request):
    """Lista todos os personagens ATIVOS do usuário."""
    # PONTO 2: Refinamento do READ para ignorar os inativos[cite: 3]
    personagens = Personagem.objects.filter(usuario=request.user, ativo=True)
    return render(request, 'lobby/lista_personagens.html', {'personagens': personagens})

@login_required
def criar_personagem(request):
    """Cria um novo personagem vinculado ao usuário[cite: 4]."""
    if request.method == 'POST':
        form = PersonagemForm(request.POST)
        if form.is_valid():
            personagem = form.save(commit=False)
            personagem.usuario = request.user
            personagem.save()
            return redirect('lista_personagens')
    else:
        form = PersonagemForm()
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Novo Personagem'})

@login_required
def editar_personagem(request, pk):
    """Edita um personagem existente[cite: 4]."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = PersonagemForm(request.POST, instance=personagem)
        if form.is_valid():
            form.save()
            return redirect('lista_personagens')
    else:
        form = PersonagemForm(instance=personagem)
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Editar Personagem'})

@login_required
def excluir_personagem(request, pk):
    """
    PONTO 3: IMPLEMENTAÇÃO DE SOFT DELETE[cite: 3]
    O personagem não é removido do banco, apenas marcado como inativo.
    """
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    if request.method == 'POST':
        personagem.ativo = False  # Soft Delete em vez de .delete()[cite: 3]
        personagem.save()
        return redirect('lista_personagens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': personagem})

# --- LÓGICA DE ROLAGENS (Entidade 3 - API & CRUD) ---

@csrf_exempt
def salvar_rolagem(request):
    """Salva o resultado e dispara o sinal de Pub-Sub via Signals[cite: 3]."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            resultado_valor = data.get('resultado')
            tipo_dado_rolado = data.get('tipo_dado', 'D20')
            personagem_id = data.get('personagem_id')
            
            personagem_instancia = None
            if personagem_id:
                personagem_instancia = Personagem.objects.filter(id=personagem_id, ativo=True).first()

            nova_rolagem = Rolagem.objects.create(
                personagem=personagem_instancia,
                jogador_nome=data.get('jogador', 'Aventureiro'),
                tipo_dado=tipo_dado_rolado,
                resultado=int(resultado_valor)
            )
            
            return JsonResponse({'status': 'sucesso', 'resultado': resultado_valor})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'metodo_nao_permitido'}, status=405)

def listar_rolagens(request):
    """
    PONTO 2: FILTROS DINÂMICOS NA API (Refinamento do READ)[cite: 3]
    Permite filtrar por tipo de dado via URL: /api/rolagens/?tipo=D20
    """
    tipo_filtro = request.GET.get('tipo')
    rolagens = Rolagem.objects.all().order_by('-data_hora')
    
    if tipo_filtro:
        rolagens = rolagens.filter(tipo_dado=tipo_filtro) # Filtro no banco[cite: 3]
    
    dados = []
    for r in rolagens[:10]:
        horario_local = timezone.localtime(r.data_hora)
        nome_exibicao = r.personagem.nome if r.personagem else r.jogador_nome
        
        dados.append({
            "jogador": nome_exibicao,
            "tipo_dado": r.tipo_dado,
            "resultado": r.resultado,
            "data": horario_local.strftime('%H:%M:%S')
        })
    
    return JsonResponse({'rolagens': dados})

@login_required
def limpar_log(request):
    """Remove todas as rolagens do log (Delete físico)[cite: 4]."""
    if request.method == 'POST':
        Rolagem.objects.all().delete()
        return JsonResponse({'status': 'sucesso', 'message': 'Log limpo com sucesso'})
    return JsonResponse({'status': 'metodo_nao_permitido'}, status=405)