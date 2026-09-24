from datetime import timedelta

from django.utils import timezone

from .models import Viagem


def notificacoes_solicitacoes(request):
    total_solicitacoes_pendentes = 0

    if request.user.is_authenticated and request.user.is_superuser:
        limite = timezone.now() - timedelta(days=30)

        total_solicitacoes_pendentes = Viagem.objects.filter(
            status="Pendente",
            criado_em__gte=limite,
        ).count()

    return {
        "total_solicitacoes_pendentes": total_solicitacoes_pendentes,
    }