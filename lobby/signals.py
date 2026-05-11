from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Rolagem, Personagem, Mesa, Item

@receiver(post_save, sender=Rolagem)
def sistema_de_combate_automatico(sender, instance, created, **kwargs):
    """
    Assinante que reage a rolagens. 
    Implementa detecção de críticos, falhas e a nova inteligência de 'Maré de Azar'[cite: 3, 4, 6].
    """
    if created:
        # Lógica para D20 (Críticos e Falhas)
        if instance.tipo_dado == 'D20':
            if instance.resultado == 20:
                print(f"🔥 SINAL DISPARADO: Crítico rolado por {instance.jogador_nome}!")
                dano_sugerido = instance.resultado * 2
                print(f"⚔️ SUGESTÃO: O dano crítico deve ser de pelo menos {dano_sugerido}!")
            elif instance.resultado == 1:
                print(f"💀 FALHA CRÍTICA: {instance.jogador_nome} tirou 1! Algo terrível pode acontecer.")

        # NOVA LÓGICA: Detecção de 'Maré de Azar' (Pé Frio)[cite: 6]
        # Busca as últimas 3 rolagens do mesmo jogador para verificar sequência negativa
        ultimas = Rolagem.objects.filter(
            jogador_nome=instance.jogador_nome
        ).order_by('-data_hora')[:3]

        if ultimas.count() == 3:
            # Se todas as 3 últimas rolagens forem menores ou iguais a 3
            if all(r.resultado <= 3 for r in ultimas):
                print(f"🎲 MARÉ DE AZAR: {instance.jogador_nome} teve 3 resultados pífios seguidos! O destino está contra você.")

@receiver(post_save, sender=Personagem)
def boas_vinda_personagem(sender, instance, created, **kwargs):
    """Sinal que reage à criação de novos personagens[cite: 4, 6]."""
    if created:
        print(f"🎭 NOVO PERSONAGEM: {instance.nome} entrou na taverna!")

@receiver(post_save, sender=Mesa)
def log_auditoria_mesa(sender, instance, created, **kwargs):
    """Log de Auditoria para novas mesas[cite: 4, 6]."""
    if created:
        print(f"📢 AUDITORIA: Nova mesa '{instance.titulo}' registrada pelo mestre {instance.mestre.username}.")

# NOVA LÓGICA: Monitoramento de Inventário (M2M Signal)[cite: 6]
@receiver(m2m_changed, sender=Personagem.itens.through)
def alerta_inventario(sender, instance, action, reverse, pk_set, **kwargs):
    """Detecta quando um personagem ganha um item valioso[cite: 6]."""
    if action == "post_add":
        for pk in pk_set:
            item = Item.objects.get(pk=pk)
            if item.valor >= 100:
                print(f"💰 RIQUEZA: {instance.nome} obteve um item valioso: {item.nome}!")