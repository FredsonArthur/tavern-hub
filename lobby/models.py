# lobby/models.py
from django.db import models
from django.utils import timezone

class Rolagem(models.Model):
    jogador = models.CharField(max_length=100, default="Aventureiro")
    tipo_dado = models.CharField(max_length=10, default="D20")
    resultado = models.IntegerField()
    data_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.jogador} tirou {self.resultado} no {self.tipo_dado}"