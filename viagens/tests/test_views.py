from datetime import time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from viagens.models import Viagem, Motorista, Carro


class ViagensViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.superuser = User.objects.create_superuser(
            username="adminuser", email="admin@semjidh.rn.gov.br", password="password123"
        )
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

        hoje = timezone.localdate()
        self.viagem1 = Viagem.objects.create(
            setor="Gabinete",
            destino="Natal Centro",
            motivo="Entrega de documentos urgentes",
            data_ida=hoje + timedelta(days=5),
            data_volta=hoje + timedelta(days=5),
            servidores="Servidor 1",
            solicitante="Diretor",
            veiculo="Carro (4 lugares)"
        )
        self.viagem2 = Viagem.objects.create(
            setor="Procon",
            destino="Parnamirim",
            motivo="Fiscalização integrada",
            data_ida=hoje + timedelta(days=10),
            data_volta=hoje + timedelta(days=11),
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
        response_desc = self.client.get(reverse('listar_viagens'), {'ordem': 'desc'})
        itens_desc = list(response_desc.context['page_obj'])
        self.assertEqual(itens_desc[0], self.viagem2)
        self.assertEqual(itens_desc[1], self.viagem1)

        response_asc = self.client.get(reverse('listar_viagens'), {'ordem': 'asc'})
        itens_asc = list(response_asc.context['page_obj'])
        self.assertEqual(itens_asc[0], self.viagem1)
        self.assertEqual(itens_asc[1], self.viagem2)

    def test_designar_motorista_e_carro_juntos(self):
        url = reverse('designar_motorista', args=[self.viagem1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Motorista Designado")
        self.assertContains(response, "Veículo da Frota")

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
        hoje = timezone.localdate()
        form_data = {
            'destino': 'Currais Novos',
            'motivo': 'Ação comunitária de juventude',
            'veiculo': 'Carro (4 lugares)',
            'data_ida': (hoje + timedelta(days=7)).strftime('%d/%m/%Y'),
            'local_partida': 'SEMJIDH',
            'data_volta': (hoje + timedelta(days=8)).strftime('%d/%m/%Y'),
            'servidores': 'Joana Silva',
            'setor': 'SEJUV',
            'solicitante': 'Coordenação SEJUV',
        }
        resp = self.client.post(url, form_data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            Viagem.objects.filter(
                destino='Currais Novos',
                motivo='Ação comunitária de juventude'
            ).exists()
        )

    def test_solicitar_viagem_emergencial_superusuario(self):
        self.client.login(username="adminuser", password="password123")
        url = reverse('solicitar_viagem')
        agora = timezone.localtime(timezone.now())
        saida = agora + timedelta(hours=3)

        form_data = {
            'destino': 'Macaíba',
            'motivo': 'Atendimento emergencial',
            'veiculo': 'Carro (4 lugares)',
            'data_ida': saida.strftime('%Y-%m-%d'),
            'horario_ida': saida.strftime('%H:%M'),
            'local_partida': 'SEMJIDH',
            'data_volta': (saida + timedelta(hours=3)).strftime('%Y-%m-%d'),
            'servidores': 'Equipe Plantão',
            'setor': 'Gabinete',
            'solicitante': 'Secretária',
        }
        resp = self.client.post(url, form_data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Viagem.objects.filter(destino='Macaíba').exists())

    def test_acao_em_massa_alterar_status(self):
        url = reverse('listar_viagens')
        resp = self.client.post(url, {
            'tipo_post': 'acao_massa',
            'acao': 'status_Cancelada',
            'viagens_ids': [self.viagem1.id, self.viagem2.id],
        })
        self.assertEqual(resp.status_code, 302)

        self.viagem1.refresh_from_db()
        self.viagem2.refresh_from_db()
        self.assertEqual(self.viagem1.status, 'Cancelada')
        self.assertEqual(self.viagem2.status, 'Cancelada')

        # Volta ambas para Pendente em massa
        self.client.post(url, {
            'tipo_post': 'acao_massa',
            'acao': 'status_Pendente',
            'viagens_ids': [self.viagem1.id, self.viagem2.id],
        })
        self.viagem1.refresh_from_db()
        self.viagem2.refresh_from_db()
        self.assertEqual(self.viagem1.status, 'Pendente')
        self.assertEqual(self.viagem2.status, 'Pendente')

    def test_acao_em_massa_apagar_envia_email_motorista(self):
        self.viagem1.motorista = self.motorista
        self.viagem1.status = 'Atribuída'
        self.viagem1.save()

        url = reverse('listar_viagens')
        resp = self.client.post(url, {
            'tipo_post': 'acao_massa',
            'acao': 'apagar',
            'viagens_ids': [self.viagem1.id, self.viagem2.id],
        })
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Viagem.objects.filter(id__in=[self.viagem1.id, self.viagem2.id]).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.motorista.email, mail.outbox[0].to)

    def test_superusuario_altera_status_individual(self):
        url = reverse('listar_viagens')

        # Usuário comum não pode alterar livremente
        resp_comum = self.client.post(url, {
            'tipo_post': 'alterar_status_individual',
            'viagem_id': self.viagem1.id,
            'status': 'Concluída',
        })
        self.assertEqual(resp_comum.status_code, 403)
        self.viagem1.refresh_from_db()
        self.assertEqual(self.viagem1.status, 'Pendente')

        # Superusuário pode alterar para qualquer status
        self.client.login(username="adminuser", password="password123")
        resp_admin = self.client.post(url, {
            'tipo_post': 'alterar_status_individual',
            'viagem_id': self.viagem1.id,
            'status': 'Concluída',
        })
        self.assertEqual(resp_admin.status_code, 302)
        self.viagem1.refresh_from_db()
        self.assertEqual(self.viagem1.status, 'Concluída')

    def test_auto_cancelar_viagens_apos_30_minutos(self):
        agora = timezone.localtime(timezone.now())
        partida_expirada = agora - timedelta(minutes=35)
        partida_recente = agora - timedelta(minutes=10)

        viagem_expirada = Viagem.objects.create(
            setor="CODIS",
            destino="Ceará-Mirim",
            motivo="Visita técnica",
            data_ida=partida_expirada.date(),
            horario_ida=partida_expirada.time().replace(second=0, microsecond=0),
            data_volta=partida_expirada.date(),
            servidores="Servidor X",
            solicitante="Gestor",
            veiculo="Carro (4 lugares)",
            status="Pendente"
        )

        viagem_recente = Viagem.objects.create(
            setor="CODIS",
            destino="São Gonçalo",
            motivo="Reunião rápida",
            data_ida=partida_recente.date(),
            horario_ida=partida_recente.time().replace(second=0, microsecond=0),
            data_volta=partida_recente.date(),
            servidores="Servidor Y",
            solicitante="Gestor",
            veiculo="Carro (4 lugares)",
            status="Pendente"
        )

        # Ao acessar listar_viagens, apenas a viagem com >30min deve ser cancelada
        self.client.get(reverse('listar_viagens'))

        viagem_expirada.refresh_from_db()
        viagem_recente.refresh_from_db()

        self.assertEqual(viagem_expirada.status, "Cancelada")
        self.assertEqual(viagem_recente.status, "Pendente")

    def test_management_command_auto_cancelar_viagens(self):
        agora = timezone.localtime(timezone.now())
        partida_expirada = agora - timedelta(minutes=45)

        viagem = Viagem.objects.create(
            setor="ASJUR",
            destino="Extremoz",
            motivo="Diligência",
            data_ida=partida_expirada.date(),
            horario_ida=partida_expirada.time().replace(second=0, microsecond=0),
            data_volta=partida_expirada.date(),
            servidores="Servidor Z",
            solicitante="Assessoria",
            veiculo="Carro (4 lugares)",
            status="Pendente"
        )

        call_command("auto_cancelar_viagens", verbosity=0)
        viagem.refresh_from_db()
        self.assertEqual(viagem.status, "Cancelada")