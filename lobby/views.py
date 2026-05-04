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
    """Renderiza a página principal com a lista de personagens para o seletor (Item 1)."""
    personagens = []
    if request.user.is_authenticated:
        personagens = Personagem.objects.filter(usuario=request.user)
    
    return render(request, 'lobby/index.html', {'personagens': personagens})

# --- CRUD DE MESA (Entidade 1) ---

@login_required
def lista_mesas(request):
    """Lista as mesas onde o usuário logado é o mestre."""
    mesas = Mesa.objects.filter(mestre=request.user)
    return render(request, 'lobby/lista_mesas.html', {'mesas': mesas})

@login_required
def criar_mesa(request):
    """Cria uma nova mesa vinculada ao mestre logado[cite: 6]."""
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
    """Lista todos os personagens do usuário logado[cite: 6]."""
    personagens = Personagem.objects.filter(usuario=request.user)
    return render(request, 'lobby/lista_personagens.html', {'personagens': personagens})

@login_required
def criar_personagem(request):
    """Cria um novo personagem associado ao usuário (Item 3 via Form)[cite: 3, 6]."""
    if request.method == 'POST':
        form = PersonagemForm(request.POST)
        if form.is_valid():
            personagem = form.save(commit=False)
            personagem.usuario = request.user
            personagem.save()
            return redirect('lista_personagens')
    else:
        # O PersonagemForm já deve conter o campo 'mesa' para a associação
        form = PersonagemForm()
    return render(request, 'lobby/form_personagem.html', {'form': form, 'titulo': 'Novo Personagem'})

@login_required
def editar_personagem(request, pk):
    """Edita um personagem existente e sua associação com mesas[cite: 3, 6]."""
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
    """Remove um personagem[cite: 6]."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    if request.method == 'POST':
        personagem.delete()
        return redirect('lista_personagens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': personagem})

# --- LÓGICA DE ROLAGENS (API) ---

@csrf_exempt
def salvar_rolagem(request):
    """Salva a rolagem vinculando-a à entidade Personagem (Item 1)[cite: 3, 6]."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            resultado_valor = data.get('resultado')
            tipo_dado_rolado = data.get('tipo_dado', 'D20')
            personagem_id = data.get('personagem_id') # Recebido do select no frontend[cite: 6]
            
            if resultado_valor is None:
                return JsonResponse({'status': 'erro', 'message': 'Resultado vazio'}, status=400)

            # Busca a instância para criar a Chave Estrangeira real
            personagem_instancia = None
            if personagem_id:
                personagem_instancia = Personagem.objects.filter(id=personagem_id).first()

            nova_rolagem = Rolagem.objects.create(
                personagem=personagem_instancia, # Vínculo técnico (Item 1)[cite: 3]
                jogador_nome=data.get('jogador', 'Aventureiro'),
                tipo_dado=tipo_dado_rolado,
                resultado=int(resultado_valor)
            )
            
            return JsonResponse({
                'status': 'sucesso', 
                'id': nova_rolagem.id,
                'resultado': resultado_valor
            })
        except Exception as e:
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'metodo_nao_permitido'}, status=405)

def listar_rolagens(request):
    """Retorna rolagens com o nome atualizado via relacionamento[cite: 6]."""
    rolagens = Rolagem.objects.all().order_by('-data_hora')[:10]
    dados = []
    for r in rolagens:
        horario_local = timezone.localtime(r.data_hora)
        # Prioriza o nome do objeto Personagem vinculado[cite: 6]
        nome_exibicao = r.personagem.nome if r.personagem else r.jogador_nome
        
        dados.append({
            "jogador": nome_exibicao,
            "tipo_dado": r.tipo_dado,
            "resultado": r.resultado,
            "data": horario_local.strftime('%d/%m/%Y %H:%M:%S')
        })
    
    return JsonResponse({'rolagens': dados})