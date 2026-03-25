# lobby/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Rolagem

def dashboard(request):
    """Renderiza a página principal do Lobby."""
    return render(request, 'lobby/index.html')

@csrf_exempt
def salvar_rolagem(request):
    """Recebe o resultado do dado via Fetch API e salva no banco de dados."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Recebido para salvar: {data}")
            
            resultado_valor = data.get('resultado')
            
            if resultado_valor is None:
                return JsonResponse({'status': 'erro', 'message': 'Resultado vazio'}, status=400)

            nova_rolagem = Rolagem.objects.create(
                jogador="Aventureiro", # No futuro, usaremos request.user.username
                tipo_dado="D20",
                resultado=int(resultado_valor)
            )
            
            return JsonResponse({'status': 'sucesso', 'id': nova_rolagem.id})
        except Exception as e:
            print(f"Erro no processamento: {e}")
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'metodo_nao_permitido'}, status=405)

def listar_rolagens(request):
    """Retorna as últimas 10 rolagens em formato JSON para o Log de Combate."""
    # Busca as 10 rolagens mais recentes (ordenadas por data decrescente)
    rolagens = Rolagem.objects.all().order_by('-data_hora')[:10]
    
    # Transforma os dados em uma lista de dicionários
    dados = [
        {
            "jogador": r.jogador,
            "resultado": r.resultado,
            "data": r.data_hora.strftime('%H:%M:%S') # Formata para apenas Hora:Minuto:Segundo
        } for r in rolagens
    ]
    
    return JsonResponse({'rolagens': dados})