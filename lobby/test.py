from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Personagem, Mesa, Rolagem

class TavernHubTest(TestCase):
    def setUp(self):
        """Configura o ambiente de teste com usuário autenticado."""
        self.client = Client()
        self.user = User.objects.create_user(username='mestre_teste', password='senha123')
        self.client.login(username='mestre_teste', password='senha123')

    def test_acesso_paginas_principais(self):
        """Verifica se as rotas principais estão respondendo com sucesso."""
        rotas = ['dashboard', 'lista_personagens', 'lista_mesas', 'criar_personagem', 'criar_mesa']
        for rota in rotas:
            response = self.client.get(reverse(rota))
            self.assertEqual(response.status_code, 200, f"Erro ao acessar {rota}")

    def test_jornada_completa_vinculada(self):
        """
        Testa a integração total das 3 entidades:
        1. Cria uma Mesa.
        2. Cria um Personagem vinculado à Mesa.
        3. Realiza uma Rolagem vinculada ao Personagem.
        """
        # 1. Criar Mesa
        mesa = Mesa.objects.create(titulo="Mesa Épica", mestre=self.user)
        
        # 2. Criar Personagem vinculado à Mesa
        personagem = Personagem.objects.create(
            nome="Legolas", 
            usuario=self.user, 
            mesa=mesa,
            classe="Arqueiro",
            raca="Elfo",
            nivel=5,
            vida_atual=40
        )
        
        # 3. Simular Rolagem via API (JSON) vinculada ao Personagem
        data_rolagem = {
            "resultado": 20,
            "jogador": "Legolas",
            "tipo_dado": "D20",
            "personagem_id": personagem.id
        }
        response = self.client.post(
            reverse('salvar_rolagem'), 
            data=data_rolagem, 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Rolagem.objects.filter(personagem=personagem, resultado=20).exists())

    def test_criacao_massa_personagens(self):
        """Testa a criação repetitiva (10 vezes) para validar a persistência."""
        for i in range(10):
            data = {
                'nome': f'Personagem de Teste {i}',
                'raca': 'Humano',
                'classe': 'Guerreiro',
                'nivel': 1,
                'vida_atual': 10,
                'historia': 'História automatizada.'
            }
            response = self.client.post(reverse('criar_personagem'), data)
            self.assertEqual(response.status_code, 302)
        
        # Verifica se o banco contém todos os registros criados
        self.assertEqual(Personagem.objects.count(), 10)

    def test_criacao_mesa(self):
        """Testa se o mestre consegue criar uma mesa via formulário[cite: 8]."""
        data = {
            'titulo': 'Mesa de Teste Automático',
            'descricao': 'Testando os requisitos do professor.'
        }
        response = self.client.post(reverse('criar_mesa'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Mesa.objects.filter(titulo='Mesa de Teste Automático').exists())