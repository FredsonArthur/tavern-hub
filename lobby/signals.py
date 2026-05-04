from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rolagem, Personagem, Mesa

@receiver(post_save, sender=Rolagem)
def sistema_de_combate_automatico(sender, instance, created, **kwargs):
    """
    Assinante que reage a rolagens. 
    Implementa a detecção de críticos e a nova lógica de sugestão de dano[cite: 3, 4].
    """
    if created and instance.tipo_dado == 'D20':
        if instance.resultado == 20:
            print(f"🔥 SINAL DISPARADO: Crítico rolado por {instance.jogador_nome}!")
            # Ponto 1: Lógica de Dano Automático (Sugestão de dano dobrado)
            dano_sugerido = instance.resultado * 2
            print(f"⚔️ SUGESTÃO: O dano crítico deve ser de pelo menos {dano_sugerido}!")
        elif instance.resultado == 1:
            print(f"💀 FALHA CRÍTICA: {instance.jogador_nome} tirou 1! Algo terrível pode acontecer.")

@receiver(post_save, sender=Personagem)
def boas_vinda_personagem(sender, instance, created, **kwargs):
    """Sinal que reage à criação de novos personagens[cite: 4]."""
    if created:
        print(f"🎭 NOVO PERSONAGEM: {instance.nome} entrou na taverna!")

@receiver(post_save, sender=Mesa)
def log_auditoria_mesa(sender, instance, created, **kwargs):
    """
    Ponto 2: Log de Auditoria. 
    Monitora a criação de novas entidades 'Mesa' no sistema.
    """
    if created:
        print(f"📢 AUDITORIA: Nova mesa '{instance.titulo}' registrada pelo mestre {instance.mestre.username}.")