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

    # ========== NOVOS CAMPOS PARA ATRIBUTOS ==========
    
    # Atributos clássicos de RPG (D&D style)
    forca = models.IntegerField(default=10, help_text="Força física, capacidade de dano e carga")
    destreza = models.IntegerField(default=10, help_text="Agilidade, reflexos e pontaria")
    constituicao = models.IntegerField(default=10, help_text="Resistência, saúde e fortitude")
    inteligencia = models.IntegerField(default=10, help_text="Raciocínio, conhecimento e lógica")
    sabedoria = models.IntegerField(default=10, help_text="Intuição, percepção e vontade")
    carisma = models.IntegerField(default=10, help_text="Persuasão, liderança e presença")
    
    # Atributos secundários (calculados automaticamente)
    pontos_vida_temporarios = models.IntegerField(default=0, help_text="PV temporários (escudos, bênçãos)")
    pontos_mana = models.IntegerField(default=0, help_text="Pontos de mana para magias")
    pontos_mana_maximo = models.IntegerField(default=0, help_text="Mana máxima")
    
    # Experiência e progressão
    xp = models.IntegerField(default=0, help_text="Pontos de experiência")
    xp_proximo_nivel = models.IntegerField(default=300, help_text="XP necessário para o próximo nível")
    
    # Status de combate
    condicoes = models.CharField(max_length=200, blank=True, help_text="Condições atuais: Envenenado, Paralisado, etc.")
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def calcular_modificador(self, atributo_valor):
        """
        Calcula o modificador de atributo seguindo a regra D&D:
        (valor - 10) // 2
        Ex: 10 = +0, 12 = +1, 14 = +2, 8 = -1
        """
        return (atributo_valor - 10) // 2
    
    def get_modificadores(self):
        """Retorna dicionário com todos os modificadores"""
        return {
            'forca': self.calcular_modificador(self.forca),
            'destreza': self.calcular_modificador(self.destreza),
            'constituicao': self.calcular_modificador(self.constituicao),
            'inteligencia': self.calcular_modificador(self.inteligencia),
            'sabedoria': self.calcular_modificador(self.sabedoria),
            'carisma': self.calcular_modificador(self.carisma),
        }
    
    def calcular_pv_maximo(self):
        """
        Calcula PV máximo baseado no nível e constituição
        Fórmula: Nível * (média do dado de vida da classe + mod Constituição)
        """
        dados_vida_por_classe = {
            'Guerreiro': 10, 'Paladino': 10, 'Bárbaro': 12,
            'Mago': 6, 'Feiticeiro': 6, 'Bruxo': 8,
            'Ladino': 8, 'Monge': 8, 'Druida': 8,
            'Clérigo': 8, 'Bardo': 8, 'Ranger': 10
        }
        dado_vida = dados_vida_por_classe.get(self.classe, 8)
        media_dado = (dado_vida + 1) // 2  # Média arredondada para cima
        mod_con = self.calcular_modificador(self.constituicao)
        
        return (media_dado + mod_con) * self.nivel
    
    def calcular_mana_maximo(self):
        """
        Calcula mana máxima baseada no nível e inteligência (para magos)
        """
        base_mana = self.nivel * 5
        mod_int = self.calcular_modificador(self.inteligencia)
        return max(0, base_mana + (mod_int * self.nivel))
    
    def curar(self, quantidade):
        """Cura o personagem e retorna a quantidade real curada"""
        curado = min(quantidade, self.vida_maxima - self.vida_atual)
        self.vida_atual += curado
        self.save()
        return curado
    
    def tomar_dano(self, quantidade):
        """Aplica dano ao personagem, considerando PV temporários"""
        dano_restante = quantidade
        
        # Primeiro, remove dos PV temporários
        if self.pontos_vida_temporarios > 0:
            absorvido = min(self.pontos_vida_temporarios, dano_restante)
            self.pontos_vida_temporarios -= absorvido
            dano_restante -= absorvido
        
        # Depois, aplica nos PV reais
        if dano_restante > 0:
            self.vida_atual -= dano_restante
        
        self.save()
        
        # Verifica se morreu
        if self.vida_atual <= 0:
            self.vida_atual = 0
            self.save()
            return {'morreu': True, 'dano': quantidade, 'vida_restante': 0}
        
        return {'morreu': False, 'dano': quantidade, 'vida_restante': self.vida_atual}
    
    def ganhar_xp(self, quantidade):
        """Adiciona XP e verifica se subiu de nível"""
        self.xp += quantidade
        subiu_nivel = False
        
        while self.xp >= self.xp_proximo_nivel:
            self.subir_nivel()
            subiu_nivel = True
            
        self.save()
        return {'subiu_nivel': subiu_nivel, 'xp_atual': self.xp, 'xp_necessario': self.xp_proximo_nivel}
    
    def subir_nivel(self):
        """Avança de nível e atualiza atributos"""
        self.nivel += 1
        self.xp -= self.xp_proximo_nivel
        
        # Recalcula PV máximo
        novo_pv_max = self.calcular_pv_maximo()
        aumento_pv = novo_pv_max - self.vida_maxima
        self.vida_maxima = novo_pv_max
        self.vida_atual += aumento_pv
        
        # Recalcula mana máximo
        novo_mana_max = self.calcular_mana_maximo()
        aumento_mana = novo_mana_max - self.pontos_mana_maximo
        self.pontos_mana_maximo = novo_mana_max
        self.pontos_mana += aumento_mana
        
        # Aumenta XP necessário para o próximo nível (20% a mais a cada nível)
        self.xp_proximo_nivel = int(self.xp_proximo_nivel * 1.2)
        
        self.save()

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