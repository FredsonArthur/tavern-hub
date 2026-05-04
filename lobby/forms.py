from django import forms
from .models import Personagem, Mesa

class PersonagemForm(forms.ModelForm):
    class Meta:
        model = Personagem
        # Adicionado 'mesa' aos campos para permitir a associação entre as entidades[cite: 3, 6]
        fields = ['mesa', 'nome', 'raca', 'classe', 'nivel', 'vida_atual', 'historia']
        widgets = {
            'mesa': forms.Select(attrs={'class': 'form-select border-primary'}), # Widget de seleção
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
        # Definimos apenas título e descrição, pois o mestre é definido automaticamente na view
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