from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rolagem, Personagem

@receiver(post_save, sender=Rolagem)
def monitorar_critico(sender, instance, created, **kwargs):
    """
    Exemplo de Pub-Sub: Quando uma Rolagem é 'publicada' no banco, 
    este assinante verifica se foi um acerto crítico[cite: 3, 5].
    """
    if created and instance.tipo_dado == 'D20' and instance.resultado == 20:
        print(f"🔥 SINAL DISPARADO: Crítico rolado por {instance.jogador_nome}!")
        # Aqui poderíamos disparar um log especial ou dar bônus automático

@receiver(post_save, sender=Personagem)
def boas_vinda_personagem(sender, instance, created, **kwargs):
    """
    Sinal que reage à criação de novos personagens.
    """
    if created:
        print(f"🎭 NOVO PERSONAGEM: {instance.nome} entrou na taverna!")