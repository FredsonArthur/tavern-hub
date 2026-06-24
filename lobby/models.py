from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import random  # Adicionado para rolagens aleatórias

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
    
    ativo = models.BooleanField(default=True, db_index=True)
    itens = models.ManyToManyField(Item, blank=True, related_name="possuidores")

    # ========== ATRIBUTOS ==========
    forca = models.IntegerField(default=10, help_text="Força física, capacidade de dano e carga")
    destreza = models.IntegerField(default=10, help_text="Agilidade, reflexos e pontaria")
    constituicao = models.IntegerField(default=10, help_text="Resistência, saúde e fortitude")
    inteligencia = models.IntegerField(default=10, help_text="Raciocínio, conhecimento e lógica")
    sabedoria = models.IntegerField(default=10, help_text="Intuição, percepção e vontade")
    carisma = models.IntegerField(default=10, help_text="Persuasão, liderança e presença")
    
    pontos_vida_temporarios = models.IntegerField(default=0, help_text="PV temporários (escudos, bênçãos)")
    pontos_mana = models.IntegerField(default=0, help_text="Pontos de mana para magias")
    pontos_mana_maximo = models.IntegerField(default=0, help_text="Mana máxima")
    
    xp = models.IntegerField(default=0, help_text="Pontos de experiência")
    xp_proximo_nivel = models.IntegerField(default=300, help_text="XP necessário para o próximo nível")
    condicoes = models.CharField(max_length=200, blank=True, help_text="Condições atuais: Envenenado, Paralisado, etc.")
    
    # ========== MÉTODOS ==========
    def calcular_modificador(self, atributo_valor):
        return (atributo_valor - 10) // 2
    
    def get_modificadores(self):
        return {
            'forca': self.calcular_modificador(self.forca),
            'destreza': self.calcular_modificador(self.destreza),
            'constituicao': self.calcular_modificador(self.constituicao),
            'inteligencia': self.calcular_modificador(self.inteligencia),
            'sabedoria': self.calcular_modificador(self.sabedoria),
            'carisma': self.calcular_modificador(self.carisma),
        }
    
    def calcular_pv_maximo(self):
        dados_vida_por_classe = {
            'Guerreiro': 10, 'Paladino': 10, 'Bárbaro': 12,
            'Mago': 6, 'Feiticeiro': 6, 'Bruxo': 8,
            'Ladino': 8, 'Monge': 8, 'Druida': 8,
            'Clérigo': 8, 'Bardo': 8, 'Ranger': 10
        }
        dado_vida = dados_vida_por_classe.get(self.classe, 8)
        media_dado = (dado_vida + 1) // 2
        mod_con = self.calcular_modificador(self.constituicao)
        return (media_dado + mod_con) * self.nivel
    
    def calcular_mana_maximo(self):
        base_mana = self.nivel * 5
        mod_int = self.calcular_modificador(self.inteligencia)
        return max(0, base_mana + (mod_int * self.nivel))
    
    def curar(self, quantidade):
        curado = min(quantidade, self.vida_maxima - self.vida_atual)
        self.vida_atual += curado
        self.save()
        return curado
    
    def tomar_dano(self, quantidade):
        dano_restante = quantidade
        if self.pontos_vida_temporarios > 0:
            absorvido = min(self.pontos_vida_temporarios, dano_restante)
            self.pontos_vida_temporarios -= absorvido
            dano_restante -= absorvido
        if dano_restante > 0:
            self.vida_atual -= dano_restante
        self.save()
        if self.vida_atual <= 0:
            self.vida_atual = 0
            self.save()
            return {'morreu': True, 'dano': quantidade, 'vida_restante': 0}
        return {'morreu': False, 'dano': quantidade, 'vida_restante': self.vida_atual}
    
    def ganhar_xp(self, quantidade):
        self.xp += quantidade
        subiu_nivel = False
        while self.xp >= self.xp_proximo_nivel:
            self.subir_nivel()
            subiu_nivel = True
        self.save()
        return {'subiu_nivel': subiu_nivel, 'xp_atual': self.xp, 'xp_necessario': self.xp_proximo_nivel}
    
    def subir_nivel(self):
        self.nivel += 1
        self.xp -= self.xp_proximo_nivel
        novo_pv_max = self.calcular_pv_maximo()
        aumento_pv = novo_pv_max - self.vida_maxima
        self.vida_maxima = novo_pv_max
        self.vida_atual += aumento_pv
        novo_mana_max = self.calcular_mana_maximo()
        aumento_mana = novo_mana_max - self.pontos_mana_maximo
        self.pontos_mana_maximo = novo_mana_max
        self.pontos_mana += aumento_mana
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
    editado = models.BooleanField(default=False)
    resultado_anterior = models.IntegerField(null=True, blank=True)
    motivo_edicao = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        nome = self.personagem.nome if self.personagem else self.jogador_nome
        status = " (Editado)" if self.editado else ""
        return f"{nome} rolou {self.tipo_dado}: {self.resultado}{status}"


# ========== SISTEMA DE COMBATE ==========

class Combate(models.Model):
    """Representa uma batalha entre heróis e inimigos"""
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name="combates")
    nome = models.CharField(max_length=100, default="⚔️ Combate")
    ativo = models.BooleanField(default=True)
    rodada = models.IntegerField(default=1)
    turno_atual = models.IntegerField(default=0)
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('preparando', 'Preparando'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparando')
    
    def __str__(self):
        return f"{self.nome} - {self.mesa.titulo} (Rodada {self.rodada})"
    
    def proximo_turno(self):
        """Avança para o próximo turno"""
        participantes = self.participantes.filter(vivo=True).order_by('ordem')
        if not participantes.exists():
            return None
        
        # Avança para o próximo participante vivo
        self.turno_atual = (self.turno_atual + 1) % participantes.count()
        
        # Se voltou ao início, incrementa a rodada
        if self.turno_atual == 0:
            self.rodada += 1
        
        self.save()
        return participantes[self.turno_atual]
    
    def finalizar(self):
        """Finaliza o combate"""
        self.status = 'concluido'
        self.data_fim = timezone.now()
        self.ativo = False
        self.save()


class ParticipanteCombate(models.Model):
    """Participante do combate (personagem ou monstro)"""
    combate = models.ForeignKey(Combate, on_delete=models.CASCADE, related_name="participantes")
    personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE, null=True, blank=True)
    
    nome = models.CharField(max_length=100)
    TIPO_CHOICES = [
        ('heroi', 'Herói'),
        ('monstro', 'Monstro'),
        ('npc', 'NPC'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='heroi')
    
    iniciativa = models.IntegerField(default=0)
    ordem = models.IntegerField(default=0)
    vivo = models.BooleanField(default=True)
    
    vida_atual = models.IntegerField(default=10)
    vida_maxima = models.IntegerField(default=10)
    
    CONDICOES = [
        ('normal', 'Normal'),
        ('envenenado', 'Envenenado'),
        ('paralisado', 'Paralisado'),
        ('confuso', 'Confuso'),
        ('cego', 'Cego'),
        ('surdo', 'Surdo'),
        ('assustado', 'Assustado'),
        ('invisivel', 'Invisível'),
    ]
    condicao = models.CharField(max_length=20, choices=CONDICOES, default='normal')
    defesa = models.IntegerField(default=10)
    
    class Meta:
        ordering = ['ordem']
    
    def __str__(self):
        status = "💀" if not self.vivo else "❤️"
        return f"{self.nome} {status} (Iniciativa: {self.iniciativa})"
    
    def aplicar_dano(self, dano):
        """Aplica dano ao participante"""
        if not self.vivo:
            return {'sucesso': False, 'mensagem': f'{self.nome} já está morto!'}
        
        self.vida_atual = max(0, self.vida_atual - dano)
        if self.vida_atual <= 0:
            self.vivo = False
            self.vida_atual = 0
        
        self.save()
        return {
            'sucesso': True,
            'vida_restante': self.vida_atual,
            'vivo': self.vivo,
            'mensagem': f'{self.nome} recebeu {dano} de dano!' if self.vivo else f'💀 {self.nome} foi derrotado!'
        }
    
    def curar(self, quantidade):
        """Cura o participante"""
        if not self.vivo:
            return {'sucesso': False, 'mensagem': f'{self.nome} está morto e não pode ser curado!'}
        
        curado = min(quantidade, self.vida_maxima - self.vida_atual)
        self.vida_atual += curado
        self.save()
        return {
            'sucesso': True,
            'curado': curado,
            'vida_atual': self.vida_atual,
            'mensagem': f'{self.nome} recuperou {curado} de vida!'
        }


class AcaoCombate(models.Model):
    """Registro de ações realizadas durante o combate"""
    participante = models.ForeignKey(ParticipanteCombate, on_delete=models.CASCADE)
    combate = models.ForeignKey(Combate, on_delete=models.CASCADE, related_name="acoes")
    rodada = models.IntegerField()
    turno = models.IntegerField()
    
    TIPO_ACOES = [
        ('ataque', 'Ataque'),
        ('defesa', 'Defesa'),
        ('magia', 'Magia'),
        ('cura', 'Cura'),
        ('especial', 'Especial'),
        ('movimento', 'Movimento'),
        ('outro', 'Outro'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_ACOES)
    descricao = models.TextField()
    alvo = models.CharField(max_length=100, null=True, blank=True)
    resultado = models.TextField(null=True, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.participante.nome} - {self.tipo} (Rodada {self.rodada})"

# ========== SISTEMA DE MISSÕES ==========

class Missao(models.Model):
    """Representa uma missão que pode ser concluída pelos jogadores"""
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name="missoes")
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    objetivos = models.TextField(help_text="Descreva os objetivos da missão")
    
    # Recompensas
    recompensa_xp = models.IntegerField(default=0)
    recompensa_ouro = models.IntegerField(default=0)
    
    # Status
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('falha', 'Falha'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    
    # Datas
    data_criacao = models.DateTimeField(default=timezone.now)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    prazo = models.DateTimeField(null=True, blank=True, help_text="Data limite para concluir a missão")
    
    # Quem criou
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name="missoes_criadas")
    
    # Dificuldade
    DIFICULDADE_CHOICES = [
        ('facil', 'Fácil'),
        ('medio', 'Médio'),
        ('dificil', 'Difícil'),
        ('epico', 'Épico'),
        ('lendario', 'Lendário'),
    ]
    dificuldade = models.CharField(max_length=20, choices=DIFICULDADE_CHOICES, default='medio')
    
    def __str__(self):
        return f"{self.titulo} - {self.mesa.titulo}"
    
    def concluir(self):
        """Conclui a missão e distribui recompensas"""
        self.status = 'concluida'
        self.data_conclusao = timezone.now()
        self.save()
        
        # Distribui recompensas para todos os personagens da mesa
        personagens = self.mesa.personagens.filter(ativo=True)
        for personagem in personagens:
            if self.recompensa_xp > 0:
                personagem.ganhar_xp(self.recompensa_xp)
        
        return {
            'xp_distribuido': self.recompensa_xp * personagens.count(),
            'personagens_afetados': personagens.count()
        }


class MissaoPersonagem(models.Model):
    """Relaciona personagens com missões (progresso individual)"""
    missao = models.ForeignKey(Missao, on_delete=models.CASCADE, related_name="progressos")
    personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE, related_name="missoes")
    
    progresso = models.IntegerField(default=0, help_text="Progresso atual da missão (0-100)")
    concluida = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    # Notas do mestre sobre este personagem na missão
    notas = models.TextField(blank=True, help_text="Notas do mestre sobre o progresso deste personagem")
    
    class Meta:
        unique_together = ['missao', 'personagem']
    
    def __str__(self):
        status = "✅" if self.concluida else "⏳"
        return f"{status} {self.personagem.nome} - {self.missao.titulo} ({self.progresso}%)"
    
    def atualizar_progresso(self, novo_progresso):
        """Atualiza o progresso da missão para este personagem"""
        self.progresso = min(100, max(0, novo_progresso))
        if self.progresso >= 100 and not self.concluida:
            self.concluida = True
            self.data_conclusao = timezone.now()
        self.save()
        return self.progresso
    
# ========== SISTEMA DE NOTIFICAÇÕES ==========

class Notificacao(models.Model):
    """Notificações para usuários sobre eventos do sistema"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificacoes")
    
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    
    TIPO_CHOICES = [
        ('info', 'Informação'),
        ('sucesso', 'Sucesso'),
        ('alerta', 'Alerta'),
        ('perigo', 'Perigo'),
        ('missao', 'Missão'),
        ('combate', 'Combate'),
        ('sistema', 'Sistema'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='info')
    
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    # Link para ação (opcional)
    link_url = models.CharField(max_length=500, blank=True, null=True)
    link_texto = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username} ({'✅' if self.lida else '🔴'})"
    
    def marcar_como_lida(self):
        self.lida = True
        self.save()