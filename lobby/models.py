from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# --- Entidade 1: Mesa (Agora com proteção por Mestre) ---
class Mesa(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    # REQUISITO: "Mesa Protegida" - Apenas o mestre gerencia a mesa
    mestre = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mesas_gerenciadas')
    data_criacao = models.DateTimeField(default=timezone.now)
    
    # Campo para definir se a mesa é privada (apenas convidados veem)
    privada = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

# --- Entidade 2: Personagem (Com Soft Delete) ---
class Personagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name="personagens")
    nome = models.CharField(max_length=100)
    raca = models.CharField(max_length=50)
    classe = models.CharField(max_length=50)
    nivel = models.IntegerField(default=1)
    vida_atual = models.IntegerField(default=10)
    historia = models.TextField(blank=True)
    
    # IMPLEMENTADO: Soft Delete
    ativo = models.BooleanField(default=True)

    def __str__(self):
        status = "" if self.ativo else " (Inativo)"
        return f"{self.nome} - Nível {self.nivel}{status}"

# --- Entidade 3: Rolagem (Agora com suporte a Rollback e Estatísticas) ---
class Rolagem(models.Model):
    personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE, null=True, blank=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, null=True, blank=True)
    
    jogador_nome = models.CharField(max_length=100, default="Aventureiro")
    tipo_dado = models.CharField(max_length=10, default="D20")
    resultado = models.IntegerField()
    data_hora = models.DateTimeField(default=timezone.now)

    # REQUISITO: "Rollback" - Armazena versão anterior em caso de erro/ajuste
    editado = models.BooleanField(default=False)
    resultado_anterior = models.IntegerField(null=True, blank=True)
    motivo_edicao = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        nome = self.personagem.nome if self.personagem else self.jogador_nome
        status = " (Editado)" if self.editado else ""
        return f"{nome} tirou {self.resultado} no {self.tipo_dado}{status}"

    class Meta:
        ordering = ['-data_hora']
        # Nome amigável no Admin do Django
        verbose_name = "Rolagem de Dado"
        verbose_name_plural = "Log de Rolagens"