from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtém um item de um dicionário usando uma chave"""
    return dictionary.get(key)

@register.filter
def get_progresso(progresso_obj):
    """Obtém o progresso de um objeto MissaoPersonagem"""
    if progresso_obj:
        return progresso_obj.progresso
    return 0