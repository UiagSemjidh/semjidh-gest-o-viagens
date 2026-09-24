from datetime import timedelta

from datetime import timedelta

from django.utils import timezone

from .models import Viagem


def notificacoes_solicitacoes(request):
    total = 0

    if request.user.is_authenticated and request.user.is_superuser:
        limite = timezone.now() - timedelta(days=30)

        total = Viagem.objects.filter(
            criado_em__gte=limite,
        ).count()

    return {
        "total_solicitacoes_pendentes": total,
    }