from django import forms
from .models import Personagem

class PersonagemForm(forms.ModelForm):
    class Meta:
        model = Personagem
        fields = ['nome', 'raca', 'classe', 'nivel', 'vida_atual', 'historia']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'raca': forms.TextInput(attrs={'class': 'form-control'}),
            'classe': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel': forms.NumberInput(attrs={'class': 'form-control'}),
            'vida_atual': forms.NumberInput(attrs={'class': 'form-control'}),
            'historia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }