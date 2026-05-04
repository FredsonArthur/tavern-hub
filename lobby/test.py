from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Personagem, Mesa

class TavernHubTest(TestCase):
    def setUp(self):
        # Configura um usuário e cliente de teste[cite: 14, 18]
        self.client = Client()
        self.user = User.objects.create_user(username='mestre_teste', password='senha123')
        self.client.login(username='mestre_teste', password='senha123')

    def test_acesso_paginas_principais(self):
        """Verifica se as rotas principais estão respondendo[cite: 16, 20]"""
        rotas = ['dashboard', 'lista_personagens', 'lista_mesas', 'criar_personagem', 'criar_mesa']
        for rota in rotas:
            response = self.client.get(reverse(rota))
            self.assertEqual(response.status_code, 200, f"Erro ao acessar {rota}")

    def test_criacao_personagem(self):
        """Testa se o sistema permite criar um personagem via formulário[cite: 15, 18, 19]"""
        data = {
            'nome': 'Aragorn',
            'raca': 'Humano',
            'classe': 'Ranger',
            'nivel': 5,
            'vida_atual': 50,
            'historia': 'Herdeiro de Isildur.'
        }
        response = self.client.post(reverse('criar_personagem'), data)
        self.assertEqual(response.status_code, 302) # Redirecionamento após sucesso[cite: 18, 20]
        self.assertTrue(Personagem.objects.filter(nome='Aragorn').exists())

    def test_criacao_mesa(self):
        """Testa se o mestre consegue criar uma mesa[cite: 15, 19, 20]"""
        data = {
            'titulo': 'Mesa de Teste Automático',
            'descricao': 'Testando os requisitos do professor.'
        }
        response = self.client.post(reverse('criar_mesa'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Mesa.objects.filter(titulo='Mesa de Teste Automático').exists())