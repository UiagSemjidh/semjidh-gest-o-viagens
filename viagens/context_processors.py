from .models import Viagem


def notificacoes_solicitacoes(request):
    total_solicitacoes_pendentes = 0

    if request.user.is_authenticated and request.user.is_superuser:
        total_solicitacoes_pendentes = Viagem.objects.filter(
            status="Pendente"
        ).count()

    return {
        "total_solicitacoes_pendentes": total_solicitacoes_pendentes,
    }