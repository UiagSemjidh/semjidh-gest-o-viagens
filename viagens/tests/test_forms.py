from django.test import TestCase
from datetime import date
from viagens.forms import ViagemForm, MotoristaForm, CarroForm

class ViagemFormTest(TestCase):
    def test_motivo_obrigatorio(self):
        # Formulário sem motivo deve ser inválido
        form_data = {
            'destino': 'Natal',
            'veiculo': 'Carro (4 lugares)',
            'data_ida': '01/12/2026',
            'local_partida': 'SEMJIDH',
            'data_volta': '02/12/2026',
            'servidores': 'Servidor 1',
            'setor': 'Gabinete',
            'solicitante': 'Chefe',
            'motivo': '',  # Vazio
        }
        form = ViagemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('motivo', form.errors)

    def test_form_valido_com_motivo(self):
        form_data = {
            'destino': 'Pau dos Ferros',
            'motivo': 'Reunião de alinhamento com conselho tutelar',
            'veiculo': 'Carro (4 lugares)',
            'data_ida': '01/12/2026',
            'local_partida': 'SEMJIDH',
            'data_volta': '02/12/2026',
            'servidores': 'Servidor A, Servidor B',
            'setor': 'Gabinete',
            'solicitante': 'Secretária',
        }
        form = ViagemForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
