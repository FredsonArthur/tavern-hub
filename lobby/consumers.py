import json
import re
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Importação tardia para evitar AppRegistryNotReady
from django.apps import apps


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer para chat em tempo real da mesa"""
    
    async def connect(self):
        self.mesa_id = self.scope['url_route']['kwargs']['mesa_id']
        self.room_group_name = f'chat_mesa_{self.mesa_id}'
        self.username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anônimo'
        
        # Verifica se o usuário está autenticado
        if not self.scope['user'].is_authenticated:
            await self.close()
            return
        
        # Verifica se o usuário pertence à mesa
        if not await self.usuario_pertence_mesa(self.scope['user'], self.mesa_id):
            await self.close()
            return
        
        # Entra no grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Envia mensagem de boas-vindas
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'🫡 {self.username} entrou na taverna!',
                'username': 'Sistema',
                'is_system': True
            }
        )
    
    async def disconnect(self, close_code):
        # Sai do grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Envia mensagem de saída
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'👋 {self.username} saiu da taverna.',
                'username': 'Sistema',
                'is_system': True
            }
        )
    
    async def receive(self, text_data):
        """Recebe mensagem do WebSocket"""
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        
        if not message:
            return
        
        # Se for comando de rolagem
        if message.startswith('/rolar'):
            await self.processar_rolagem(message)
            return
        
        # Mensagem normal
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.username,
                'is_system': False
            }
        )
    
    async def chat_message(self, event):
        """Envia mensagem para o WebSocket"""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'is_system': event.get('is_system', False),
            'timestamp': event.get('timestamp', '')
        }))
    
    async def processar_rolagem(self, message):
        """Processa comandos de rolagem (/rolar 1d20)"""
        # Parse do comando
        match = re.search(r'/rolar\s+(\d+)d(\d+)', message)
        if not match:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'❌ Formato inválido! Use: /rolar [quantidade]d[faces] (ex: /rolar 1d20)',
                    'username': 'Sistema',
                    'is_system': True
                }
            )
            return
        
        quantidade = int(match.group(1))
        faces = int(match.group(2))
        
        # Limita rolagens para evitar spam
        if quantidade > 10:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'❌ Máximo de 10 dados por rolagem!',
                    'username': 'Sistema',
                    'is_system': True
                }
            )
            return
        
        if faces not in [4, 6, 8, 10, 12, 20, 100]:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'❌ Dados suportados: D4, D6, D8, D10, D12, D20, D100',
                    'username': 'Sistema',
                    'is_system': True
                }
            )
            return
        
        # Rola os dados
        resultados = [random.randint(1, faces) for _ in range(quantidade)]
        total = sum(resultados)
        rolagem_str = ' + '.join(map(str, resultados))
        
        # Verifica críticos
        criticos = [r for r in resultados if r == faces]
        falhas = [r for r in resultados if r == 1]
        
        msg = f'🎲 **{self.username}** rolou {quantidade}d{faces}:\n'
        msg += f'📊 {rolagem_str}'
        if quantidade > 1:
            msg += f'\n📈 **Total: {total}**'
        if criticos:
            msg += f'\n🎉 **CRÍTICO!** ({len(criticos)}x {faces})'
        if falhas:
            msg += f'\n💀 **FALHA!** ({len(falhas)}x 1)'
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg,
                'username': '🎲 Dados',
                'is_system': True
            }
        )
    
    @database_sync_to_async
    def usuario_pertence_mesa(self, user, mesa_id):
        """Verifica se o usuário pertence à mesa usando importação tardia"""
        # Importa os modelos aqui para evitar AppRegistryNotReady
        User = apps.get_model('auth', 'User')
        Mesa = apps.get_model('lobby', 'Mesa')
        Personagem = apps.get_model('lobby', 'Personagem')
        
        try:
            mesa = Mesa.objects.get(id=mesa_id)
            # Verifica se é o mestre ou tem personagem na mesa
            if user == mesa.mestre:
                return True
            return Personagem.objects.filter(usuario=user, mesa=mesa, ativo=True).exists()
        except Mesa.DoesNotExist:
            return False