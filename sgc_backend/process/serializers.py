from rest_framework import serializers
from .models import ProcesoTareaMap, TipoDeProcesoGeneral,\
Proceso,\
EstadoEjecucion,\
DisparadorEjecucion,\
EjecucionProceso,\
TipoLog,\
LogEjecucionProceso,\
TareaProceso,\
LogEjecucionTareaProceso
from accounts.serializers import UserSerializer


class TareaSerializer(serializers.ModelSerializer):    
    class Meta:
        model = TareaProceso
        fields = '__all__'

class ProcesoTareaMapSerializer(serializers.ModelSerializer):
    tarea = TareaSerializer(read_only=True)
    class Meta:
        model = ProcesoTareaMap
        fields = ['tarea', 'orden']

class EjecucionProcesoListSerializer(serializers.ModelSerializer):
    usuario=UserSerializer(read_only=True)
    tareas = serializers.SerializerMethodField()

    class Meta:
        model=EjecucionProceso
        fields='__all__'
        depth=1
    def get_tareas(self,obj):        
        tareas = ProcesoTareaMap.objects.filter(proceso=obj.proceso).order_by('orden')
        #tareas_proceso = TareaProceso.objects.filter(id__in=tareas)
        return ProcesoTareaMapSerializer(tareas ,many=True, context=self.context).data
 
class LogEjecucionProcesoListSerializer(serializers.ModelSerializer):    
    class Meta:
        model=LogEjecucionProceso
        fields=['id','mensaje','fecha','tipo']
        depth=1