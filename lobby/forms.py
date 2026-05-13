from django import forms
from .models import Personagem, Mesa, Item

class PersonagemForm(forms.ModelForm):
    class Meta:
        model = Personagem
        # Mantém a associação com 'mesa' conforme configurado anteriormente
        fields = ['mesa', 'nome', 'raca', 'classe', 'nivel', 'vida_atual', 'historia']
        widgets = {
            'mesa': forms.Select(attrs={'class': 'form-select border-primary'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'raca': forms.TextInput(attrs={'class': 'form-control'}),
            'classe': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel': forms.NumberInput(attrs={'class': 'form-control'}),
            'vida_atual': forms.NumberInput(attrs={'class': 'form-control'}),
            'historia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'raridade': forms.Select(attrs={'class': 'form-select'}),
        }