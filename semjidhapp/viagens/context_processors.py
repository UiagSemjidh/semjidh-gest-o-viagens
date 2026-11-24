from django.utils import timezone

from .models import Viagem


def notificacoes_solicitacoes(request):
    total = 0

    if request.user.is_authenticated and request.user.is_superuser:
        hoje = timezone.localdate()

        total = Viagem.objects.filter(
            status="Pendente",
            data_volta__gte=hoje,
        ).count()

    return {
        "total_solicitacoes_pendentes": total,
    }