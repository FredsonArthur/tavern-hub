from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Entidade 1: Mesa (Onde os jogadores se reúnem)
class Mesa(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    mestre = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mesas_gerenciadas')
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titulo

# Entidade 2: Personagem (Atributos do jogador)
class Personagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    raca = models.CharField(max_length=50)
    classe = models.CharField(max_length=50)
    nivel = models.IntegerField(default=1)
    vida_atual = models.IntegerField(default=10)
    historia = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nome} - Nível {self.nivel}"

# Entidade 3: Rolagem (Agora vinculada a Personagem e Mesa para o Log)
class Rolagem(models.Model):
    # Relacionamos a rolagem a um personagem e a uma mesa específica
    personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE, null=True, blank=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, null=True, blank=True)
    
    # Campos base para o registro dos dados
    jogador_nome = models.CharField(max_length=100, default="Aventureiro")
    tipo_dado = models.CharField(max_length=10, default="D20")
    resultado = models.IntegerField()
    data_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        # Mostra o nome do personagem se existir, senão usa o nome padrão
        nome = self.personagem.nome if self.personagem else self.jogador_nome
        return f"{nome} tirou {self.resultado} no {self.tipo_dado}"

    class Meta:
        ordering = ['-data_hora']