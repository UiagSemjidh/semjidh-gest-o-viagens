from datetime import datetime, time, timedelta
from django import forms
from django.utils import timezone
from .models import Viagem, Motorista, Carro


class ViagemForm(forms.ModelForm):
    data_ida = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
        error_messages={'required': 'A data de saída é obrigatória.'},
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}
        )
    )
    data_volta = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
        error_messages={'required': 'A data de retorno é obrigatória.'},
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}
        )
    )
    processo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite o número de processo, se houver',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['data_ida'].required = True
        self.fields['data_volta'].required = True

    class Meta:
        model = Viagem
        fields = [
            'destino', 'motivo', 'veiculo', 'data_ida', 'local_partida',
            'horario_ida', 'data_volta', 'horario_volta', 'servidores',
            'setor', 'solicitante', 'processo'
        ]
        widgets = {
            'destino': forms.TextInput(attrs={
                'placeholder': 'Digite para onde será a viagem',
                'type': 'text',
                'class': 'form-control'
            }),
            'motivo': forms.Textarea(attrs={
                'placeholder': 'Descreva detalhadamente a justificativa e o motivo da viagem',
                'rows': 3,
                'class': 'form-control'
            }),
            'veiculo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'local_partida': forms.TextInput(attrs={
                'placeholder': 'Qual ponto inicial da viagem?',
                'type': 'text',
                'class': 'form-control'
            }),
            'horario_ida': forms.TimeInput(format='%H:%M', attrs={
                'placeholder': 'HH:MM',
                'type': 'time',
                'class': 'form-control'
            }),
            'horario_volta': forms.TimeInput(format='%H:%M', attrs={
                'placeholder': 'HH:MM',
                'type': 'time',
                'class': 'form-control'
            }),
            'servidores': forms.TextInput(attrs={
                'placeholder': 'Digite os nomes dos servidores separados por vírgula',
                'class': 'form-control'
            }),
            'setor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'solicitante': forms.TextInput(attrs={
                'placeholder': 'Digite o nome do solicitante',
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_ida = cleaned_data.get('data_ida')
        horario_ida = cleaned_data.get('horario_ida')
        data_volta = cleaned_data.get('data_volta')

        is_superuser = bool(self.user and self.user.is_authenticated and self.user.is_superuser)

        if data_ida and not is_superuser:
            agora = timezone.localtime(timezone.now())
            limite_minimo = agora + timedelta(hours=48)

            hora_saida = horario_ida or time.min
            dt_saida = timezone.make_aware(
                datetime.combine(data_ida, hora_saida),
                timezone.get_current_timezone(),
            )

            if dt_saida < limite_minimo:
                data_sugerida = limite_minimo.strftime('%d/%m/%Y às %H:%M')
                self.add_error(
                    'data_ida',
                    f'A solicitação deve ser feita com pelo menos 48 horas de antecedência '
                    f'(a partir de {data_sugerida}).'
                )

        if data_ida and data_volta and data_volta < data_ida:
            self.add_error(
                'data_volta',
                'A data de retorno não pode ser anterior à data de saída.'
            )

        return cleaned_data


class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['nome', 'email', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Nome do Motorista',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email do Motorista',
                'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': 'Telefone do Motorista',
                'class': 'form-control',
                'inputmode': 'tel',
            })
        }


class CarroForm(forms.ModelForm):
    class Meta:
        model = Carro
        fields = ['marca', 'modelo', 'placa']
        widgets = {
            'marca': forms.TextInput(attrs={
                'placeholder': 'Marca do carro',
                'class': 'form-control'
            }),
            'modelo': forms.TextInput(attrs={
                'placeholder': 'Modelo do carro',
                'class': 'form-control'
            }),
            'placa': forms.TextInput(attrs={
                'placeholder': 'Placa do carro',
                'class': 'form-control'
            })
        }