from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Rolagem, Personagem, Mesa, Item


@receiver(post_save, sender=Rolagem)
def sistema_de_combate_automatico(sender, instance, created, **kwargs):
    """
    Assinante que reage a rolagens. 
    Implementa detec��o de cr�ticos, falhas e a intelig�ncia de 'Mar� de Azar'.
    """
    if created:
        # L�gica para D20 (Cr�ticos e Falhas)
        if instance.tipo_dado == 'D20':
            if instance.resultado == 20:
                print(f"? SINAL DISPARADO: Cr�tico rolado por {instance.jogador_nome}!")
                dano_sugerido = instance.resultado * 2
                print(f"?? SUGEST�O: O dano cr�tico deve ser de pelo menos {dano_sugerido}!")
            elif instance.resultado == 1:
                print(f"? FALHA CR�TICA: {instance.jogador_nome} tirou 1! Algo terr�vel pode acontecer.")

        # DETEC��O DE 'MAR� DE AZAR' (P� Frio)
        # Busca as �ltimas 3 rolagens do mesmo jogador para verificar sequ�ncia negativa
        ultimas = Rolagem.objects.filter(
            jogador_nome=instance.jogador_nome
        ).order_by('-data_hora')[:3]

        if ultimas.count() == 3:
            # Se todas as 3 �ltimas rolagens forem menores ou iguais a 3
            if all(r.resultado <= 3 for r in ultimas):
                print(
                    f"? MAR� DE AZAR: {instance.jogador_nome} teve 3 resultados p�fios seguidos! O destino est� contra voc�.")


@receiver(post_save, sender=Personagem)
def boas_vinda_personagem(sender, instance, created, **kwargs):
    """Sinal que reage � cria��o de novos personagens."""
    if created:
        print(f"? NOVO PERSONAGEM: {instance.nome} entrou na taverna!")


@receiver(post_save, sender=Mesa)
def log_auditoria_mesa(sender, instance, created, **kwargs):
    """Log de Auditoria para novas mesas."""
    if created:
        print(f"? AUDITORIA: Nova mesa '{instance.titulo}' registrada pelo mestre {instance.mestre.username}.")


@receiver(m2m_changed, sender=Personagem.itens.through)
def alerta_inventario(sender, instance, action, reverse, pk_set, **kwargs):
    """
    Monitoramento de Invent�rio (M2M Signal)
    Detecta quando um personagem ganha itens de alta raridade usando uma query otimizada.
    """
    if action == "post_add" and pk_set:
        # OTIMIZA��O: Busca todos os itens adicionados de uma s� vez usando o operador __in,
        # eliminando m�ltiplas requisi��es repetitivas ao banco de dados.
        itens_adicionados = Item.objects.filter(pk__in=pk_set)

        for item in itens_adicionados:
            if item.raridade in ['Raro', '�pico', 'Lend�rio']:
                print(
                    f"? ALERTA DE RIQUEZA: O personagem '{instance.nome}' adicionou o item '{item.nome}' ({item.raridade}) ao invent�rio!")