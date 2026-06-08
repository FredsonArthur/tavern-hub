from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# --- ENTIDADE: Item (Sistema de Inventário Many-to-Many) ---
class Item(models.Model):
    """Representa itens que podem ser equipados ou carregados por personagens."""
    
    RARIDADE_CHOICES = [
        ('Comum', 'Comum'),
        ('Incomum', 'Incomum'),
        ('Raro', 'Raro'),
        ('Épico', 'Épico'),
        ('Lendário', 'Lendário'),
    ]

    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    raridade = models.CharField(
        max_length=20, 
        choices=RARIDADE_CHOICES, 
        default='Comum'
    )
    # Adicionado db_index para acelerar as buscas de Soft Delete
    ativo = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.nome} ({self.raridade})"


# --- Entidade 1: Mesa ---
class Mesa(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    mestre = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mesas_mestrada")
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titulo


# --- Entidade 2: Personagem ---
class Personagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personagens")
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name="personagens", null=True, blank=True)
    
    nome = models.CharField(max_length=100)
    raca = models.CharField(max_length=50)
    classe = models.CharField(max_length=50)
    nivel = models.IntegerField(default=1)
    vida_maxima = models.IntegerField(default=10)
    vida_atual = models.IntegerField(default=10)
    historia = models.TextField(blank=True)
    
    # IMPLEMENTADO: Soft Delete com índice para performance
    ativo = models.BooleanField(default=True, db_index=True)

    # IMPLEMENTADO: Relacionamento Many-to-Many para Inventário
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

    # REQUISITO: "Rollback" - Auditoria de dados
    editado = models.BooleanField(default=False)
    resultado_anterior = models.IntegerField(null=True, blank=True)
    motivo_edicao = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        nome = self.personagem.nome if self.personagem else self.jogador_nome
        status = " (Editado)" if self.editado else ""
        return f"{nome} rolou {self.tipo_dado}: {self.resultado}{status}"