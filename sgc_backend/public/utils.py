from .models import TipoDeDocumento
def getTipoPersona(tpidentif):
    tipo_documento = TipoDeDocumento.objects.get(tipoDocumento=tpidentif)
    tipo_persona = tipo_documento.idTipoPersona.tipoPersona
    return tipo_persona