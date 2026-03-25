# lobby/models.py
from django.db import models
from django.utils import timezone

class Rolagem(models.Model):
    # Campo para armazenar o nome do personagem/jogador
    jogador = models.CharField(max_length=100, default="Aventureiro")
    
    # Campo para armazenar o tipo de dado (D4, D6, D20, etc.)
    tipo_dado = models.CharField(max_length=10, default="D20")
    
    # Valor obtido na rolagem
    resultado = models.IntegerField()
    
    # Data e hora do registro para ordenação no Log de Combate
    data_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        # Representação amigável no Admin do Django
        return f"{self.jogador} tirou {self.resultado} no {self.tipo_dado}"