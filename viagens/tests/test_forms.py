from datetime import datetime, time, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from viagens.forms import ViagemForm


class ViagemFormTest(TestCase):
    def setUp(self):
        self.user_comum = User.objects.create_user(
            username="comum", password="password123"
        )
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.data_futura_ida = (timezone.localdate() + timedelta(days=5)).strftime("%Y-%m-%d")
        self.data_futura_volta = (timezone.localdate() + timedelta(days=6)).strftime("%Y-%m-%d")

    def _dados_base(self):
        return {
            'destino': 'Pau dos Ferros',
            'motivo': 'Reunião de alinhamento com conselho tutelar',
            'veiculo': 'Carro (4 lugares)',
            'data_ida': self.data_futura_ida,
            'local_partida': 'SEMJIDH',
            'horario_ida': '08:00',
            'data_volta': self.data_futura_volta,
            'horario_volta': '17:00',
            'servidores': 'Servidor A, Servidor B',
            'setor': 'Gabinete',
            'solicitante': 'Secretária',
        }

    def test_motivo_obrigatorio(self):
        form_data = self._dados_base()
        form_data['motivo'] = ''
        form = ViagemForm(data=form_data, user=self.user_comum)
        self.assertFalse(form.is_valid())
        self.assertIn('motivo', form.errors)

    def test_form_valido_com_motivo(self):
        form = ViagemForm(data=self._dados_base(), user=self.user_comum)
        self.assertTrue(form.is_valid(), form.errors)

    def test_data_ida_e_data_volta_obrigatorias(self):
        form_data = self._dados_base()
        form_data['data_ida'] = ''
        form_data['data_volta'] = ''
        form = ViagemForm(data=form_data, user=self.user_comum)
        self.assertFalse(form.is_valid())
        self.assertIn('data_ida', form.errors)
        self.assertIn('data_volta', form.errors)

    def test_data_volta_anterior_a_data_ida_invalida(self):
        form_data = self._dados_base()
        data_ida = timezone.localdate() + timedelta(days=6)
        data_volta = timezone.localdate() + timedelta(days=5)
        form_data['data_ida'] = data_ida.strftime("%Y-%m-%d")
        form_data['data_volta'] = data_volta.strftime("%Y-%m-%d")

        form = ViagemForm(data=form_data, user=self.user_comum)
        self.assertFalse(form.is_valid())
        self.assertIn('data_volta', form.errors)

    def test_bloqueia_menos_de_48_horas_para_usuario_comum(self):
        agora = timezone.localtime(timezone.now())
        saida_curta = agora + timedelta(hours=24)

        form_data = self._dados_base()
        form_data['data_ida'] = saida_curta.strftime("%Y-%m-%d")
        form_data['horario_ida'] = saida_curta.strftime("%H:%M")
        form_data['data_volta'] = (saida_curta + timedelta(hours=6)).strftime("%Y-%m-%d")

        form = ViagemForm(data=form_data, user=self.user_comum)
        self.assertFalse(form.is_valid())
        self.assertIn('data_ida', form.errors)

    def test_permite_menos_de_48_horas_para_superusuario(self):
        agora = timezone.localtime(timezone.now())
        saida_emergencial = agora + timedelta(hours=4)

        form_data = self._dados_base()
        form_data['data_ida'] = saida_emergencial.strftime("%Y-%m-%d")
        form_data['horario_ida'] = saida_emergencial.strftime("%H:%M")
        form_data['data_volta'] = (saida_emergencial + timedelta(hours=4)).strftime("%Y-%m-%d")

        form = ViagemForm(data=form_data, user=self.superuser)
        self.assertTrue(form.is_valid(), form.errors)