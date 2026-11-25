from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Viagem, Motorista, Carro
from .forms import ViagemForm, MotoristaForm, CarroForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
import csv
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django import forms
from django.views.decorators.http import require_POST
from viagens.management.commands.auto_cancelar_viagens import cancelar_viagens_expiradas



@login_required
def listar_viagens(request):
    # Cancela automaticamente viagens pendentes que passaram de 30 min da partida
    cancelar_viagens_expiradas()

    # ==========================================================
    # PROCESSAMENTO DE POST NA PRÓPRIA PÁGINA (SEM ABRIR OUTRA URL)
    # ==========================================================
    if request.method == "POST":
        tipo_post = request.POST.get("tipo_post", "")
        status_validos = dict(Viagem.STATUS_CHOICES).keys()

        # 1. Ações em massa
        if tipo_post == "acao_massa":
            viagens_ids = request.POST.getlist("viagens_ids")
            acao = request.POST.get("acao", "").strip()

            if not viagens_ids:
                messages.warning(request, "Nenhuma viagem foi selecionada.")
            else:
                viagens_qs = Viagem.objects.select_related("motorista").filter(id__in=viagens_ids)
                total = viagens_qs.count()

                if total == 0:
                    messages.warning(request, "As viagens selecionadas não foram encontradas.")
                elif acao == "apagar":
                    for viagem in viagens_qs:
                        if viagem.motorista and viagem.motorista.email:
                            try:
                                send_mail(
                                    "VIAGEM CANCELADA!",
                                    (
                                        f"Uma viagem foi cancelada.\n"
                                        f"Viagem do dia {viagem.data_ida.strftime('%d/%m/%Y')} "
                                        f"de destino {viagem.destino} foi cancelada."
                                    ),
                                    settings.DEFAULT_FROM_EMAIL,
                                    [viagem.motorista.email],
                                    fail_silently=True,
                                )
                            except Exception:
                                pass

                    viagens_qs.delete()
                    messages.success(
                        request,
                        f"{total} viage{'m foi apagada' if total == 1 else 'ns foram apagadas'} com sucesso."
                    )
                elif acao.startswith("status_"):
                    novo_status = acao.replace("status_", "", 1)
                    if novo_status in status_validos:
                        viagens_qs.update(status=novo_status)
                        messages.success(
                            request,
                            f"Status de {total} viage{'m alterado' if total == 1 else 'ns alterado'} para '{novo_status}'."
                        )
                    else:
                        messages.error(request, "Status inválido.")
                else:
                    messages.error(request, "Ação em massa inválida.")

        # 2. Alteração individual de status pelo superusuário
        elif tipo_post == "alterar_status_individual":
            if not request.user.is_superuser:
                return HttpResponseForbidden("Apenas superusuários podem alterar o status livremente.")

            viagem_id = request.POST.get("viagem_id")
            novo_status = request.POST.get("status", "").strip()

            if novo_status in status_validos and viagem_id:
                viagem = get_object_or_404(Viagem, id=viagem_id)
                viagem.status = novo_status
                viagem.save(update_fields=["status"])
                messages.success(
                    request,
                    f"Status da viagem para {viagem.destino} alterado para '{novo_status}'."
                )
            else:
                messages.error(request, "Não foi possível alterar o status.")

        query_string = request.GET.urlencode()
        url_destino = f"{request.path}?{query_string}" if query_string else request.path
        return redirect(url_destino)

    # ==========================================================
    # LISTAGEM E FILTROS (GET)
    # ==========================================================
    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "")
    setor = request.GET.get("setor", "")
    motorista_id = request.GET.get("motorista", "")
    ordem = request.GET.get("ordem", "desc")

    cadastro_de = request.GET.get("cadastro_de", "")
    cadastro_ate = request.GET.get("cadastro_ate", "")
    saida_de = request.GET.get("saida_de", "")
    saida_ate = request.GET.get("saida_ate", "")

    order_field = "data_ida" if ordem == "asc" else "-data_ida"

    viagens = Viagem.objects.select_related(
        "motorista",
        "carro",
    ).order_by(order_field)

    if busca:
        viagens = viagens.filter(
            Q(destino__icontains=busca)
            | Q(processo__icontains=busca)
            | Q(setor__icontains=busca)
            | Q(solicitante__icontains=busca)
            | Q(servidores__icontains=busca)
            | Q(veiculo__icontains=busca)
            | Q(motorista__nome__icontains=busca)
        )

    if status:
        viagens = viagens.filter(status=status)

    if setor:
        viagens = viagens.filter(setor=setor)

    if motorista_id:
        viagens = viagens.filter(motorista_id=motorista_id)

    if cadastro_de:
        try:
            data_inicial = datetime.strptime(cadastro_de, "%Y-%m-%d").date()
            inicio = timezone.make_aware(
                datetime.combine(data_inicial, time.min)
            )
            viagens = viagens.filter(criada_em__gte=inicio)
        except ValueError:
            pass

    if cadastro_ate:
        try:
            data_final = datetime.strptime(cadastro_ate, "%Y-%m-%d").date()
            fim = timezone.make_aware(
                datetime.combine(data_final, time.max)
            )
            viagens = viagens.filter(criada_em__lte=fim)
        except ValueError:
            pass

    if saida_de:
        try:
            viagens = viagens.filter(data_ida__gte=saida_de)
        except ValueError:
            pass

    if saida_ate:
        try:
            viagens = viagens.filter(data_ida__lte=saida_ate)
        except ValueError:
            pass

    paginator = Paginator(viagens, 20)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    filtros = request.GET.copy()
    filtros.pop("page", None)

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "busca": busca,
        "status_selecionado": status,
        "ordem": ordem,
        "setor_selecionado": setor,
        "motorista_selecionado": int(motorista_id) if motorista_id.isdigit() else None,
        "cadastro_de": cadastro_de,
        "cadastro_ate": cadastro_ate,
        "saida_de": saida_de,
        "saida_ate": saida_ate,
        "setores": Viagem.SETOR_CHOICES,
        "status_choices": Viagem.STATUS_CHOICES,
        "motoristas": Motorista.objects.order_by("nome"),
        "filtros_query": filtros.urlencode(),
    }

    return render(request, "viagens/listar_viagens.html", context)

def editar_motorista(request, motorista_id):
    motorista = get_object_or_404(Motorista, id=motorista_id)

    if request.method == "POST":
        form = MotoristaForm(request.POST, instance=motorista)

        if form.is_valid():
            form.save()
            messages.success(request, "Dados do motorista atualizados com sucesso.")
            return redirect("listar_motoristas")
    else:
        form = MotoristaForm(instance=motorista)

    return render(
        request,
        "viagens/editar_motorista.html",
        {
            "form": form,
            "motorista": motorista,
        },
    )

def solicitar_viagem(request):
    if request.method == 'POST':
        form = ViagemForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Viagem solicitada com sucesso!')
            form = ViagemForm(user=request.user)
            return render(request, 'viagens/solicitar_viagem.html', {'form': form})
    else:
        form = ViagemForm(user=request.user)

    return render(request, 'viagens/solicitar_viagem.html', {'form': form})

@login_required
def designar_motorista(request, viagem_id):
    viagem = get_object_or_404(Viagem, id=viagem_id)
    motoristas = Motorista.objects.all().order_by("nome")
    carros = Carro.objects.all().order_by("modelo")

    if request.method == 'POST':
        motorista_id = request.POST.get('motorista')
        carro_id = request.POST.get('carro')

        if motorista_id:
            viagem.motorista = get_object_or_404(Motorista, id=motorista_id)
        else:
            viagem.motorista = None

        if carro_id:
            viagem.carro = get_object_or_404(Carro, id=carro_id)
        else:
            viagem.carro = None

        if viagem.motorista or viagem.carro:
            viagem.status = 'Atribuída'
        else:
            viagem.status = 'Pendente'

        viagem.save()
        messages.success(request, 'Motorista e Veículo atualizados com sucesso!')
        return redirect('listar_viagens')

    return render(
        request,
        'viagens/designar_motorista.html',
        {
            'viagem': viagem,
            'motoristas': motoristas,
            'carros': carros,
        }
    )

@login_required
def cadastrar_motorista(request):
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            form.save()  # Salva o motorista no banco de dados
            
            messages.success(request, 'Motorista cadastrado com sucesso!')
            return redirect('listar_motoristas')  # Redireciona para a página de listagem dos motoristas
    else:
        form = MotoristaForm()
    
    return render(request, 'viagens/cadastrar_motorista.html', {'form': form})

@login_required
def listar_motoristas(request):
    motoristas = Motorista.objects.all()
    return render(request, 'viagens/listar_motorista.html', {'motoristas': motoristas})

def home(request):
    return render(request, "viagens/home.html")

@login_required
def apagar_viagem(request, id):
    viagem = get_object_or_404(Viagem, id=id)

    if request.method == 'POST':
        # Armazena os dados necessários antes de deletar a viagem
        data_ida_str = viagem.data_ida.strftime('%d/%m/%Y')
        destino = viagem.destino
        # Verifica se há motorista associado e obtém o e-mail, se existir
        motorista_email = viagem.motorista.email if viagem.motorista else None

        # Deleta a viagem
        viagem.delete()

        # Se a viagem estiver designada (ou seja, tiver motorista), envia o e-mail
        if motorista_email:
            assunto = "VIAGEM CANCELADA!"
            corpo_email = (
                f"Uma viagem foi cancelada.\n"
                f"Viagem do dia {data_ida_str} de destino {destino} foi cancelada."
            )
            send_mail(
                assunto,
                corpo_email,
                settings.DEFAULT_FROM_EMAIL,
                [motorista_email],
                fail_silently=False,
            )
        return redirect('listar_viagens')  # Redireciona para a lista de viagens

    # Para requisições GET, exibe a tela de confirmação
    return render(request, 'confirmar_apagar.html', {'viagem': viagem})

@login_required
def apagar_motorista(request, id):
    motorista = get_object_or_404(Motorista, id=id)

    if request.method == 'POST':
        motorista.delete()
        return redirect('listar_motoristas')
    

@login_required
def exportar_viagens(request):
    viagens = Viagem.objects.select_related(
        "motorista",
        "carro",
    ).order_by("-data_ida")

    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "")
    setor = request.GET.get("setor", "")
    motorista_id = request.GET.get("motorista", "")
    cadastro_de = request.GET.get("cadastro_de", "")
    cadastro_ate = request.GET.get("cadastro_ate", "")
    saida_de = request.GET.get("saida_de", "")
    saida_ate = request.GET.get("saida_ate", "")

    if busca:
        viagens = viagens.filter(
            Q(destino__icontains=busca)
            | Q(processo__icontains=busca)
            | Q(setor__icontains=busca)
            | Q(solicitante__icontains=busca)
            | Q(servidores__icontains=busca)
            | Q(veiculo__icontains=busca)
            | Q(motorista__nome__icontains=busca)
        )

    if status:
        viagens = viagens.filter(status=status)

    if setor:
        viagens = viagens.filter(setor=setor)

    if motorista_id:
        viagens = viagens.filter(motorista_id=motorista_id)

    if cadastro_de:
        try:
            data_inicial = datetime.strptime(cadastro_de, "%Y-%m-%d").date()
            inicio = timezone.make_aware(
                datetime.combine(data_inicial, time.min)
            )
            viagens = viagens.filter(criada_em__gte=inicio)
        except ValueError:
            pass

    if cadastro_ate:
        try:
            data_final = datetime.strptime(cadastro_ate, "%Y-%m-%d").date()
            fim = timezone.make_aware(
                datetime.combine(data_final, time.max)
            )
            viagens = viagens.filter(criada_em__lte=fim)
        except ValueError:
            pass

    if saida_de:
        try:
            viagens = viagens.filter(data_ida__gte=saida_de)
        except ValueError:
            pass

    if saida_ate:
        try:
            viagens = viagens.filter(data_ida__lte=saida_ate)
        except ValueError:
            pass

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="viagens_semjidh.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Destino", "Data de Ida", "Data de Volta", "Solicitante", "Motorista"])

    for viagem in viagens:
        writer.writerow([
            viagem.id,
            viagem.destino,
            viagem.data_ida.strftime("%d/%m/%Y"),
            viagem.data_volta.strftime("%d/%m/%Y"),
            viagem.solicitante,
            viagem.motorista.nome if viagem.motorista else "Sem motorista",
        ])

    return response

@login_required
def cadastrar_carro(request):
    if request.method == 'POST':
        form = CarroForm(request.POST)
        if form.is_valid():
            form.save()  # Salva o carro no banco de dados
            
            messages.success(request, 'Carro cadastrado com sucesso!')
            return redirect('listar_carros')  # Redireciona para a página de listagem dos carro
    else:
        form = CarroForm()
    
    return render(request, 'viagens/cadastrar_carro.html', {'form': form})

@login_required
def listar_carros(request):
    carros = Carro.objects.all()
    return render(request, 'viagens/listar_carro.html', {'carros': carros})

@login_required
def apagar_carro(request, id):
    carro = get_object_or_404(Carro, id=id)

    if request.method == 'POST':
        carro.delete()
        return redirect('listar_carros')

@login_required
def designar_carro(request, viagem_id):
    viagem = Viagem.objects.get(id=viagem_id)
    carros = Carro.objects.all()
    if request.method == 'POST':
        carro_id = request.POST.get('carro')
        carro = Carro.objects.get(id=carro_id)
        viagem.carro = carro
        viagem.status = 'Atribuída'
        viagem.save()  
        messages.success(request, 'Carro designado com sucesso!')
        return redirect('listar_viagens')
    return render(request, 'viagens/designar_carro.html', {'viagem': viagem, 'carros': carros})

def atualizar_volta_real(request, viagem_id):
    if request.method == "POST":
        viagem = get_object_or_404(Viagem, id=viagem_id)
        valor = request.POST.get("horario_volta_real")

        if valor:
            try:
                data_hora = forms.DateTimeField(
                    input_formats=[
                        "%Y-%m-%dT%H:%M",
                        "%Y-%m-%dT%H:%M:%S",
                    ]
                ).clean(valor)
            except ValidationError:
                return HttpResponseBadRequest(
                    "Informe uma data e um horário válidos."
                )

            viagem.horario_volta_real = data_hora
            viagem.save(update_fields=["horario_volta_real"])

    return redirect("listar_viagens")