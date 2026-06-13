from django import forms
from .models import Personagem, Mesa, Item

class PersonagemForm(forms.ModelForm):
    # Definição das escolhas para raça
    RACA_CHOICES = [
        ('Humano', '🧑 Humano'),
        ('Elfo', '🧝 Elfo'),
        ('Anão', '⛏️ Anão'),
        ('Halfling', '🍃 Halfling'),
        ('Gnomo', '🔧 Gnomo'),
        ('Tiefling', '👿 Tiefling'),
        ('Meio-Elfo', '💫 Meio-Elfo'),
        ('Meio-Orc', '💪 Meio-Orc'),
        ('Dragonborn', '🐉 Dragonborn'),
    ]
    
    # Definição das escolhas para classe
    CLASSE_CHOICES = [
        ('Guerreiro', '⚔️ Guerreiro'),
        ('Mago', '🔮 Mago'),
        ('Ladino', '🗡️ Ladino'),
        ('Clérigo', '🙏 Clérigo'),
        ('Bárbaro', '🪓 Bárbaro'),
        ('Paladino', '🛡️ Paladino'),
        ('Druida', '🌿 Druida'),
        ('Bardo', '🎵 Bardo'),
        ('Feiticeiro', '✨ Feiticeiro'),
        ('Bruxo', '🔗 Bruxo'),
        ('Monge', '🥋 Monge'),
        ('Ranger', '🏹 Ranger'),
    ]
    
    # Sobrescrevendo os campos para usar ChoiceField
    raca = forms.ChoiceField(choices=RACA_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    classe = forms.ChoiceField(choices=CLASSE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Personagem
        fields = ['mesa', 'nome', 'raca', 'classe', 'nivel', 'vida_atual', 'historia',
                  'forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma']
        widgets = {
            'mesa': forms.Select(attrs={'class': 'form-select border-primary'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sir Arthur, Merlin, Kratos...'}),
            'nivel': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'value': 1}),
            'vida_atual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Deixe em branco para calcular automaticamente'}),
            'historia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva a história, motivações e background do seu personagem...'}),
            
            # Atributos
            'forca': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30, 'value': 10}),
            'destreza': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30, 'value': 10}),
            'constituicao': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30, 'value': 10}),
            'inteligencia': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30, 'value': 10}),
            'sabedoria': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30, 'value': 10}),
            'carisma': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30, 'value': 10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurações adicionais
        self.fields['vida_atual'].required = False
        self.fields['vida_atual'].help_text = "Deixe em branco para calcular automaticamente baseado no nível e constituição"
        self.fields['mesa'].required = False
        self.fields['mesa'].empty_label = "Selecione uma mesa (opcional)"


class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['titulo', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: Crônicas de Arton'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Descreva o cenário e as regras da sua mesa...'
            }),
        }


class ItemForm(forms.ModelForm):
    """Formulário para criação de itens no sistema."""
    
    RARIDADE_CHOICES = [
        ('Comum', '📦 Comum'),
        ('Incomum', '✨ Incomum'),
        ('Raro', '⭐ Raro'),
        ('Épico', '🌟 Épico'),
        ('Lendário', '🏆 Lendário'),
    ]
    
    raridade = forms.ChoiceField(choices=RARIDADE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Item
        fields = ['nome', 'descricao', 'peso', 'raridade']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: Espada Longa +1'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Propriedades mágicas e detalhes...'
            }),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Peso em kg'}),
        }