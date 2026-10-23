from .models import EventoAuditoria


def registrar(
    categoria,
    accion,
    resultado,
    actor=None,
    objetivo_id=None,
    referencia="",
    detalle="",
):
    return EventoAuditoria.objects.create(
        categoria=categoria,
        accion=accion,
        resultado=resultado,
        actor=actor,
        objetivo_id=objetivo_id,
        referencia=str(referencia)[:50],
        detalle=str(detalle)[:200],
    )
