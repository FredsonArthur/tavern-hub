from .models import Notificacao

def criar_notificacao(usuario, titulo, mensagem, tipo='info', link_url=None, link_texto=None):
    """Cria uma notificação para um usuário"""
    return Notificacao.objects.create(
        usuario=usuario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        link_url=link_url,
        link_texto=link_texto
    )

def criar_notificacao_para_mesa(mesa, titulo, mensagem, tipo='info', link_url=None, link_texto=None):
    """Cria notificações para todos os personagens de uma mesa"""
    from .models import Personagem
    
    notificacoes = []
    personagens = Personagem.objects.filter(mesa=mesa, ativo=True)
    usuarios = set(p.usuario for p in personagens)
    
    # Adiciona o mestre também
    usuarios.add(mesa.mestre)
    
    for usuario in usuarios:
        notificacoes.append(
            Notificacao.objects.create(
                usuario=usuario,
                titulo=titulo,
                mensagem=mensagem,
                tipo=tipo,
                link_url=link_url,
                link_texto=link_texto
            )
        )
    
    return notificacoes

def notificacoes_nao_lidas(usuario):
    """Retorna a quantidade de notificações não lidas de um usuário"""
    return Notificacao.objects.filter(usuario=usuario, lida=False).count()