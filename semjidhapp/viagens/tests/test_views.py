from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from viagens.models import Viagem, Motorista, Carro

class ViagensViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        self.motorista = Motorista.objects.create(
            nome="Motorista Teste",
            email="teste@motorista.com",
            telefone="84988887777"
        )
        self.carro = Carro.objects.create(
            marca="Fiat",
            modelo="Cronos",
            placa="BRA2E19"
        )
        self.viagem1 = Viagem.objects.create(
            setor="Gabinete",
            destino="Natal Centro",
            motivo="Entrega de documentos urgentes",
            data_ida=date(2026, 11, 10),
            data_volta=date(2026, 11, 10),
            servidores="Servidor 1",
            solicitante="Diretor",
            veiculo="Carro (4 lugares)"
        )
        self.viagem2 = Viagem.objects.create(
            setor="Procon",
            destino="Parnamirim",
            motivo="Fiscalização integrada",
            data_ida=date(2026, 12, 20),
            data_volta=date(2026, 12, 21),
            servidores="Fiscal A",
            solicitante="Coordenador",
            veiculo="Carro (4 lugares)"
        )

    def test_listar_viagens_status_e_motivo(self):
        response = self.client.get(reverse('listar_viagens'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Entrega de documentos urgentes")
        self.assertContains(response, "Fiscalização integrada")

    def test_filtro_ordenacao_data(self):
        # Ordem decrescente (padrão)
        response_desc = self.client.get(reverse('listar_viagens'), {'ordem': 'desc'})
        itens_desc = list(response_desc.context['page_obj'])
        self.assertEqual(itens_desc[0], self.viagem2)
        self.assertEqual(itens_desc[1], self.viagem1)

        # Ordem crescente
        response_asc = self.client.get(reverse('listar_viagens'), {'ordem': 'asc'})
        itens_asc = list(response_asc.context['page_obj'])
        self.assertEqual(itens_asc[0], self.viagem1)
        self.assertEqual(itens_asc[1], self.viagem2)

    def test_designar_motorista_e_carro_juntos(self):
        url = reverse('designar_motorista', args=[self.viagem1.id])
        # GET deve carregar ambos
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Motorista Designado")
        self.assertContains(response, "Veículo da Frota")

        # POST deve salvar motorista e carro juntos
        post_data = {
            'motorista': self.motorista.id,
            'carro': self.carro.id
        }
        resp_post = self.client.post(url, post_data)
        self.assertEqual(resp_post.status_code, 302)

        self.viagem1.refresh_from_db()
        self.assertEqual(self.viagem1.motorista, self.motorista)
        self.assertEqual(self.viagem1.carro, self.carro)
        self.assertEqual(self.viagem1.status, 'Atribuída')

    def test_solicitar_viagem_post_sucesso(self):
        url = reverse('solicitar_viagem')
        form_data = {
            'destino': 'Currais Novos',
            'motivo': 'Ação comunitária de juventude',
            'veiculo': 'Carro (4 lugares)',
            'data_ida': '15/12/2026',
            'local_partida': 'SEMJIDH',
            'data_volta': '16/12/2026',
            'servidores': 'Joana Silva',
            'setor': 'SEJUV',
            'solicitante': 'Coordenação SEJUV',
        }
        resp = self.client.post(url, form_data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Viagem.objects.filter(destino='Currais Novos', motivo='Ação comunitária de juventude').exists())
