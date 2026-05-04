import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Rolagem, Personagem, Mesa
from .forms import PersonagemForm

# --- VIEWS DE NAVEGAÇÃO ---

def dashboard(request):
    """Renderiza a página principal do Lobby."""
    return render(request, 'lobby/index.html')

# --- CRUD DE PERSONAGEM (Entidade 2) ---

@login_required
def lista_personagens(request):
    """Lista todos os personagens do usuário logado (Read)."""
    personagens = Personagem.objects.filter(usuario=request.user)
    return render(request, 'lobby/lista_personagens.html', {'personagens': personagens})

@login_required
def criar_personagem(request):
    """Cria um novo personagem vinculado ao usuário (Create)."""
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
    """Edita um personagem existente (Update)."""
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
    """Remove um personagem (Delete)."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    if request.method == 'POST':
        personagem.delete()
        return redirect('lista_personagens')
    return render(request, 'lobby/confirmar_exclusao.html', {'objeto': personagem})

# --- LÓGICA DE ROLAGENS (API) ---

@csrf_exempt
def salvar_rolagem(request):
    """Recebe o resultado e salva no banco."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            resultado_valor = data.get('resultado')
            nome_jogador = data.get('jogador', 'Aventureiro')
            tipo_dado_rolado = data.get('tipo_dado', 'D20')
            
            if resultado_valor is None:
                return JsonResponse({'status': 'erro', 'message': 'Resultado vazio'}, status=400)

            nova_rolagem = Rolagem.objects.create(
                jogador_nome=nome_jogador,
                tipo_dado=tipo_dado_rolado,
                resultado=int(resultado_valor)
            )
            
            return JsonResponse({
                'status': 'sucesso', 
                'id': nova_rolagem.id,
                'jogador': nome_jogador,
                'resultado': resultado_valor
            })
        except Exception as e:
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'metodo_nao_permitido'}, status=405)

def listar_rolagens(request):
    """Retorna as últimas 10 rolagens em formato JSON."""
    rolagens = Rolagem.objects.all().order_by('-data_hora')[:10]
    dados = []
    for r in rolagens:
        horario_local = timezone.localtime(r.data_hora)
        nome_exibicao = r.personagem.nome if r.personagem else r.jogador_nome
        
        dados.append({
            "jogador": nome_exibicao,
            "tipo_dado": r.tipo_dado,
            "resultado": r.resultado,
            "data": horario_local.strftime('%d/%m/%Y %H:%M:%S')
        })
    
    return JsonResponse({'rolagens': dados})