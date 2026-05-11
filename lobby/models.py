from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# --- NOVA ENTIDADE: Item (Para Sistema de Inventário Many-to-Many) ---
class Item(models.Model):
    """Representa itens que podem ser equipados ou carregados por personagens[cite: 3]."""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    valor = models.IntegerField(default=0, help_text="Valor em moedas de ouro")

    def __str__(self):
        return self.nome

# --- Entidade 1: Mesa ---
class Mesa(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    # REQUISITO: "Mesa Protegida" - Apenas o mestre gerencia a mesa[cite: 3]
    mestre = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mesas_gerenciadas')
    data_criacao = models.DateTimeField(default=timezone.now)
    privada = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

# --- Entidade 2: Personagem (Com Soft Delete e Inventário) ---
class Personagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name="personagens")
    nome = models.CharField(max_length=100)
    raca = models.CharField(max_length=50)
    classe = models.CharField(max_length=50)
    nivel = models.IntegerField(default=1)
    vida_atual = models.IntegerField(default=10)
    historia = models.TextField(blank=True)
    
    # IMPLEMENTADO: Soft Delete[cite: 3]
    ativo = models.BooleanField(default=True)

    # IMPLEMENTADO: Relacionamento Many-to-Many para Inventário[cite: 3]
    itens = models.ManyToManyField(Item, blank=True, related_name="possuidores")

    def __str__(self):
        status = "" if self.ativo else " (Inativo)"
        return f"{self.nome} - Nível {self.nivel}{status}"

# --- Entidade 3: Rolagem ---
class Rolagem(models.Model):
    personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE, null=True, blank=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, null=True, blank=True)
    
    jogador_nome = models.CharField(max_length=100, default="Aventureiro")
    tipo_dado = models.CharField(max_length=10, default="D20")
    resultado = models.IntegerField()
    data_hora = models.DateTimeField(default=timezone.now)

    # REQUISITO: "Rollback" - Auditoria de dados[cite: 3]
    editado = models.BooleanField(default=False)
    resultado_anterior = models.IntegerField(null=True, blank=True)
    motivo_edicao = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        nome = self.personagem.nome if self.personagem else self.jogador_nome
        status = " (Editado)" if self.editado else ""
        return f"{nome} tirou {self.resultado} no {self.tipo_dado}{status}"

    class Meta:
        ordering = ['-data_hora']
        verbose_name = "Rolagem de Dado"
        verbose_name_plural = "Log de Rolagens"