# lobby/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Rolagem

def dashboard(request):
    return render(request, 'lobby/index.html')

@csrf_exempt
def salvar_rolagem(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Recebido: {data}") # Isso vai aparecer no seu terminal do VS Code
            
            # Mudança: Usar data.get para evitar erro se a chave estiver vazia
            resultado_valor = data.get('resultado')
            
            if resultado_valor is None:
                return JsonResponse({'status': 'erro', 'message': 'Resultado vazio'}, status=400)

            nova_rolagem = Rolagem.objects.create(
                jogador="Aventureiro",
                tipo_dado="D20",
                resultado=int(resultado_valor) # Garante que é um número inteiro
            )
            
            return JsonResponse({'status': 'sucesso', 'id': nova_rolagem.id})
        except Exception as e:
            print(f"Erro no processamento: {e}")
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'metodo_nao_permitido'}, status=405)