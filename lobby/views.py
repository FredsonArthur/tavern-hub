# lobby/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone  # Importação necessária para conversão de fuso horário
from .models import Rolagem

def dashboard(request):
    """Renderiza a página principal do Lobby."""
    return render(request, 'lobby/index.html')

@csrf_exempt
def salvar_rolagem(request):
    """Recebe o resultado, o nome do jogador e o tipo de dado via Fetch API e salva no banco de dados."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Recebido para salvar: {data}")
            
            resultado_valor = data.get('resultado')
            # Captura o nome do jogador enviado pelo JavaScript ou usa o padrão
            nome_jogador = data.get('jogador', 'Aventureiro')
            # Captura o tipo de dado enviado pelo JavaScript ou usa D20 como padrão
            tipo_dado_rolado = data.get('tipo_dado', 'D20')
            
            if resultado_valor is None:
                return JsonResponse({'status': 'erro', 'message': 'Resultado vazio'}, status=400)

            # Cria o registro utilizando os dados dinâmicos enviados pelo widget
            nova_rolagem = Rolagem.objects.create(
                jogador=nome_jogador,
                tipo_dado=tipo_dado_rolado,
                resultado=int(resultado_valor)
            )
            
            return JsonResponse({
                'status': 'sucesso', 
                'id': nova_rolagem.id,
                'jogador': nome_jogador,
                'tipo_dado': tipo_dado_rolado
            })
        except Exception as e:
            print(f"Erro no processamento: {e}")
            return JsonResponse({'status': 'erro', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'metodo_nao_permitido'}, status=405)

def listar_rolagens(request):
    """Retorna as últimas 10 rolagens em formato JSON com data e horário corrigidos para Brasília."""
    # Busca as 10 rolagens mais recentes (ordenadas por data decrescente)
    rolagens = Rolagem.objects.all().order_by('-data_hora')[:10]
    
    # Transforma os objetos em uma lista de dicionários para o Log
    dados = []
    for r in rolagens:
        # localtime() converte o horário UTC do banco para o fuso horário local
        horario_local = timezone.localtime(r.data_hora)
        
        dados.append({
            "jogador": r.jogador,
            "tipo_dado": r.tipo_dado,
            "resultado": r.resultado,
            # Atualizado para incluir a data (dia/mês/ano) e o horário
            "data": horario_local.strftime('%d/%m/%Y %H:%M:%S') 
        })
    
    return JsonResponse({'rolagens': dados})