from datetime import datetime, time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from viagens.models import Viagem


def cancelar_viagens_expiradas():
    """
    Cancela viagens com status 'Pendente' que já passaram de 30 minutos
    após a data e horário de partida.
    """
    agora = timezone.localtime(timezone.now())
    limite = agora - timedelta(minutes=30)

    pendentes = Viagem.objects.filter(
        status="Pendente",
        data_ida__lte=limite.date(),
    )

    ids_para_cancelar = []
    for viagem in pendentes:
        hora_partida = viagem.horario_ida or time.min
        dt_partida = timezone.make_aware(
            datetime.combine(viagem.data_ida, hora_partida),
            timezone.get_current_timezone(),
        )
        if dt_partida <= limite:
            ids_para_cancelar.append(viagem.id)

    if ids_para_cancelar:
        return Viagem.objects.filter(id__in=ids_para_cancelar).update(status="Cancelada")
    return 0


class Command(BaseCommand):
    help = "Cancela automaticamente viagens pendentes 30 minutos após o horário de partida."

    def handle(self, *args, **options):
        count = cancelar_viagens_expiradas()

        if options.get("verbosity", 1) >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{count} viagem(ns) cancelada(s) automaticamente."
                )
            )