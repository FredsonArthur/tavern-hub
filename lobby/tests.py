import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Personagem, Mesa, Rolagem, Item


class TavernHubTests(TestCase):
    def setUp(self):
        """
        CONFIGURA��O DE AMBIENTE (Base para Testes de Integra��o)
        Prepara usu�rios, mesas e itens para os cen�rios abaixo.
        """
        self.client = Client()

        # Cria��o de usu�rios (Mestre e Jogador Comum)
        self.mestre = User.objects.create_user(username='mestre_supremo', password='123')
        self.invasor = User.objects.create_user(username='invasor', password='123')

        # Entidade 1: Mesa
        self.mesa = Mesa.objects.create(titulo="Mesa de Testes", mestre=self.mestre)

        # Entidade 2: Personagem (CORRIGIDO: Removidas as barras invertidas acidentais)
        self.personagem = Personagem.objects.create(
            nome="Gimli", usuario=self.mestre, mesa=self.mesa, classe="Guerreiro", raca="Anao"
        )

        # Utilizando 'raridade' ao inv�s de 'valor' para bater com o models.py atualizado
        self.machado = Item.objects.create(nome="Machado Duplo", raridade="Raro", peso=5.0)

    # --- 1. TESTES DE UNIDADE (Unit Tests) ---
    def test_model_str_representations(self):
        """Valida se as strings dos modelos est�o corretas para o Admin."""
        self.assertEqual(str(self.mesa), "Mesa de Testes")
        self.assertEqual(str(self.personagem), "Gimli - N�vel 1")
        self.assertEqual(str(self.machado), "Machado Duplo (Raro)")

    # --- 2. TESTES DE INTEGRA��O (API de Rolagens) ---
    def test_fluxo_salvamento_rolagem_api(self):
        """Simula o dado rolando no front e salvando no back via JSON."""
        dados_rolagem = {
            "resultado": 18,
            "jogador": "Gimli",
            "tipo_dado": "D20",
            "personagem_id": self.personagem.id
        }

        # Envia requisi��o POST ass�ncrona (JSON)
        response = self.client.post(
            reverse('salvar_rolagem'),
            data=json.dumps(dados_rolagem),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Rolagem.objects.count(), 1)

        # Garante que o v�nculo autom�tico com a mesa do personagem aconteceu
        rolagem_salva = Rolagem.objects.first()
        self.assertEqual(rolagem_salva.mesa, self.mesa)

    # --- 3. GEST�O DE INVENT�RIO (Many-to-Many & Signals) ---
    def test_inventario_m2m_e_signals(self):
        """Garante que o relacionamento M2M funciona e o sinal de raridade n�o quebra a grava��o."""
        self.personagem.itens.add(self.machado)

        # Verifica se o item foi corretamente associado ao her�i
        self.assertIn(self.machado, self.personagem.itens.all())
        self.assertEqual(self.machado.possuidores.first(), self.personagem)

    # --- 4. CONTROLADORES DE SEGURAN�A (Mesa Protegida & Rollback) ---
    def test_protecao_rollback_mestre(self):
        """Garante que APENAS o mestre da mesa pode editar uma rolagem (Seguran�a)."""
        rolagem = Rolagem.objects.create(
            personagem=self.personagem,
            mesa=self.mesa,
            jogador_nome="Gimli",
            tipo_dado="D20",
            resultado=1
        )

        # Tenta editar usando o usu�rio invasor
        self.client.login(username='invasor', password='123')
        response = self.client.post(reverse('rollback_rolagem', args=[rolagem.id]), {'novo_resultado': 20})

        # Deve retornar erro 403 (Proibido) conforme nossa View
        self.assertEqual(response.status_code, 403)

        # Tenta editar com o mestre real
        self.client.login(username='mestre_supremo', password='123')
        response = self.client.post(reverse('rollback_rolagem', args=[rolagem.id]),
                                    {'novo_resultado': 20, 'motivo': 'Erro de digita��o'})
        self.assertEqual(response.status_code, 302)  # Redireciona ap�s sucesso

    # --- 5. TESTES DE REGRESS�O (Garantir que o Soft Delete continua funcionando) ---
    def test_soft_delete_permanece_ativo(self):
        """Confirma que o personagem inativo n�o aparece na lista p�blica (Fase 3)."""
        self.client.login(username='mestre_supremo', password='123')
        self.personagem.ativo = False
        self.personagem.save()

        response = self.client.get(reverse('lista_personagens'))
        self.assertNotContains(response, "Gimli")

    # --- 6. TESTES DE CARGA/ESTAT�STICAS (Aggregation) ---
    def test_estatisticas_com_massa_de_dados(self):
        """Cria v�rias rolagens e verifica se a m�dia (Aggregation) est� correta."""
        Rolagem.objects.create(resultado=10, jogador_nome="A")
        Rolagem.objects.create(resultado=20, jogador_nome="B")

        self.client.login(username='mestre_supremo', password='123')
        response = self.client.get(reverse('painel_estatisticas'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stats']['total_rolagens'], 2)
        self.assertEqual(response.context['stats']['media_geral'], 15.0)