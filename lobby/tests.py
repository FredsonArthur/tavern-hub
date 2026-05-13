import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Personagem, Mesa, Rolagem, Item

class TavernHubTests(TestCase):
    def setUp(self):
        """
        CONFIGURAÇÃO DE AMBIENTE (Base para Testes de Integração)
        Prepara usuários, mesas e itens para os cenários abaixo.
        """
        self.client = Client()
        
        # Criação de usuários (Mestre e Jogador Comum)
        self.mestre = User.objects.create_user(username='mestre_supremo', password='123')
        self.invasor = User.objects.create_user(username='invasor', password='123')
        
        # Entidade 1: Mesa
        self.mesa = Mesa.objects.create(titulo="Mesa de Testes", mestre=self.mestre)
        
        # Entidade 2: Personagem
        self.personagem = Personagem.objects.create(
            nome="Gimli", usuario=self.mestre, mesa=self.mesa, classe="Guerreiro", raca="Anão"
        )
        
        # Nova Entidade: Item (Many-to-Many)
        self.machado = Item.objects.create(nome="Machado Duplo", valor=150, peso=5.0)

    # --- 1. TESTES DE UNIDADE (Unit Tests) ---
    def test_model_str_representations(self):
        """Valida se as strings dos modelos estão corretas para o Admin."""
        self.assertEqual(str(self.mesa), "Mesa de Testes")
        self.assertEqual(str(self.personagem), "Gimli - Nível 1")
        self.assertEqual(str(self.machado), "Machado Duplo")

    # --- 2. TESTES DE INTEGRAÇÃO (Many-to-Many & Signals) ---
    def test_inventario_m2m_e_signals(self):
        """Garante que o relacionamento M2M funciona e o sinal de 'Riqueza' não quebra a gravação."""
        self.personagem.itens.add(self.machado)
        self.assertEqual(self.personagem.itens.count(), 1)
        self.assertIn(self.machado, self.personagem.itens.all())

    # --- 3. TESTES DE SISTEMA (End-to-End Simulado via API) ---
    def test_fluxo_salvamento_rolagem_api(self):
        """Simula o dado rolando no front e salvando no back via JSON."""
        data = {
            "resultado": 20,
            "jogador": "Gimli",
            "tipo_dado": "D20",
            "personagem_id": self.personagem.id
        }
        response = self.client.post(
            reverse('salvar_rolagem'), 
            data=json.dumps(data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Rolagem.objects.filter(resultado=20).exists())

    # --- 4. TESTES DE SEGURANÇA (Permissions) ---
    def test_protecao_rollback_mestre(self):
        """Garante que APENAS o mestre da mesa pode editar uma rolagem (Segurança)."""
        rolagem = Rolagem.objects.create(resultado=10, mesa=self.mesa, jogador_nome="Gimli")
        
        # Tenta editar com um usuário que não é o mestre
        self.client.login(username='invasor', password='123')
        response = self.client.post(reverse('rollback_rolagem', args=[rolagem.id]), {'novo_resultado': 20})
        
        # Deve retornar erro 403 (Proibido) conforme nossa View
        self.assertEqual(response.status_code, 403)
        
        # Tenta editar com o mestre real
        self.client.login(username='mestre_supremo', password='123')
        response = self.client.post(reverse('rollback_rolagem', args=[rolagem.id]), {'novo_resultado': 20, 'motivo': 'Erro de digitação'})
        self.assertEqual(response.status_code, 302) # Redireciona após sucesso

    # --- 5. TESTES DE REGRESSÃO (Garantir que o Soft Delete continua funcionando) ---
    def test_soft_delete_permanece_ativo(self):
        """Confirma que o personagem inativo não aparece na lista pública (Fase 3)."""
        self.client.login(username='mestre_supremo', password='123')
        self.personagem.ativo = False
        self.personagem.save()
        
        response = self.client.get(reverse('lista_personagens'))
        self.assertNotContains(response, "Gimli")

    # --- 6. TESTES DE CARGA/ESTATÍSTICAS (Aggregation) ---
    def test_estatisticas_com_massa_de_dados(self):
        """Cria várias rolagens e verifica se a média (Aggregation) está correta."""
        Rolagem.objects.create(resultado=10, jogador_nome="A")
        Rolagem.objects.create(resultado=20, jogador_nome="B")
        
        self.client.login(username='mestre_supremo', password='123')
        response = self.client.get(reverse('painel_estatisticas'))
        
        # Média de (10+20)/2 = 15.0
        self.assertContains(response, "15,0")