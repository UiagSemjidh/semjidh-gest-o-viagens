from django import forms
from .models import Viagem, Motorista, Carro

class ViagemForm(forms.ModelForm):
    data_ida = forms.DateField(
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'})
    )
    data_volta = forms.DateField(
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Viagem
        fields = ['destino', 'motivo', 'veiculo', 'data_ida', 'local_partida', 'horario_ida', 'data_volta', 'horario_volta', 'servidores', 'setor', 'solicitante', 'processo']
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
            'data_ida': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
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
            'data_volta': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
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
            'processo': forms.TextInput(attrs={
                'placeholder': 'Digite o número de processo, se houver',
                'class': 'form-control'
            })
        }
        processo = forms.CharField(required=False)

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
                "inputmode": "tel",
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