from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date
from viagens.models import Viagem, Motorista, Carro

class ViagemModelTest(TestCase):
    def setUp(self):
        self.motorista = Motorista.objects.create(
            nome="Carlos Silva",
            email="carlos@example.com",
            telefone="84999998888"
        )
        self.carro = Carro.objects.create(
            marca="Toyota",
            modelo="Corolla",
            placa="ABC1D23"
        )

    def test_criar_viagem_com_motivo(self):
        viagem = Viagem.objects.create(
            setor="Gabinete",
            destino="Mossoró",
            motivo="Audiência pública sobre direitos humanos",
            data_ida=date(2026, 12, 1),
            data_volta=date(2026, 12, 3),
            servidores="Maria, João",
            solicitante="Diretoria",
            veiculo="Carro (4 lugares)"
        )
        self.assertEqual(viagem.status, "Pendente")
        self.assertEqual(viagem.motivo, "Audiência pública sobre direitos humanos")
        self.assertEqual(len(viagem.servidores_lista), 2)
        self.assertIn("Mossoró", str(viagem))

    def test_designar_motorista_e_carro(self):
        viagem = Viagem.objects.create(
            setor="SPM",
            destino="Caicó",
            motivo="Capacitação regional",
            data_ida=date(2026, 12, 5),
            data_volta=date(2026, 12, 6),
            servidores="Ana",
            solicitante="Coordenadoria",
            veiculo="Carro (4 lugares)"
        )
        viagem.motorista = self.motorista
        viagem.carro = self.carro
        viagem.status = "Atribuída"
        viagem.save()

        viagem.refresh_from_db()
        self.assertEqual(viagem.motorista.nome, "Carlos Silva")
        self.assertEqual(viagem.carro.placa, "ABC1D23")
        self.assertEqual(viagem.status, "Atribuída")
