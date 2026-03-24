# lobby/views.py
from django.shortcuts import render

def dashboard(request):
    # Por enquanto, apenas renderiza o HTML
    return render(request, 'lobby/index.html')