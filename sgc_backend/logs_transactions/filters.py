import django_filters
from .models import Log_Cambios_Update

class LogCambiosUpdateFilter(django_filters.FilterSet):
    timestamp = django_filters.DateTimeFromToRangeFilter(field_name='TiempoAccion')

    class Meta:
        model = Log_Cambios_Update
        fields = ['timestamp']