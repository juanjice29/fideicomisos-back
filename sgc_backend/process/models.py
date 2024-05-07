from django.db import models
from accounts.models import User

class TipoDeProcesoGeneral(models.Model):
    nombre = models.CharField(max_length=100,verbose_name='Nombre de proceso general')
    acronimo = models.CharField(max_length=10,verbose_name='Acronimo de proceso general')
    descripcion = models.TextField(verbose_name='Descripcion del proceso tipo de proceso general')

    class Meta:
        db_table = 'PRCS_TIPO_PROCESO_GENERAL'

class Proceso(models.Model):
    tipoProceso = models.ForeignKey(TipoDeProcesoGeneral, on_delete=models.CASCADE,db_column='tipo_proceso', verbose_name='Tipo de Proceso general en el que encaja este proceso')
    nombre = models.CharField(max_length=100,verbose_name='Nombre de proceso')
    acronimo=models.CharField(max_length=15,verbose_name='Acronimo de proceso')
    funcionRelacionada=models.CharField(max_length=100,verbose_name='Funcion en el codigo que tiene el decorador de proceso',db_column='funcion_relacionada')
    descripcion = models.TextField(verbose_name='Descripcion general del proceso')
    stakeholders = models.CharField(max_length=100,verbose_name='Stakeholder involucrados del proceso')
    modulosInvolucrados = models.CharField(max_length=100,db_column='modulos_involucrados',verbose_name='Modulos de datos que seran necesarios para ejecutar el proceso')

    class Meta:
        db_table = 'PRCS_PROCESO'
class EstadoEjecucion(models.Model):
    nombre = models.CharField(max_length=100,verbose_name='Nombre de estado de ejecucion')
    acronimio = models.CharField(max_length=10,verbose_name='Acronimo de estado de ejecucion')
    descripcion = models.TextField(verbose_name='Descripcion del estado de ejecucion')
    class Meta:
        db_table = 'PRCS_ESTADO_EJECUCION'

class DisparadorEjecucion(models.Model):
    nombre = models.CharField(max_length=100,verbose_name='Nombre de disparador de ejecucion')
    acronimo = models.CharField(max_length=10,verbose_name='Acronimo de disparador de ejecucion')
    descripcion = models.TextField(verbose_name='Descripcion del disparador de ejecucion')
    class Meta:
        db_table = 'PRCS_DISPARADOR_EJECUCION'

class EjecucionProceso(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, verbose_name='Proceso asociado a esta ejecucion')    
    fechaInicio = models.DateTimeField(verbose_name='Fecha de inicio de la ejecución',db_column='fecha_inicio')
    fechaFin = models.DateTimeField(null=True,verbose_name='Fecha de fin de la ejecución',db_column='fecha_fin')
    estadoEjecucion=models.ForeignKey(EstadoEjecucion, on_delete=models.CASCADE, verbose_name='Estado de la ejecución de este proceso',db_column='estado_ejecucion')
    resultado = models.TextField(verbose_name='Resultado de la ejecución del proceso')
    disparador = models.ForeignKey(DisparadorEjecucion, on_delete=models.CASCADE, verbose_name='Disparador de la ejecución de este proceso')
    usuario =models.ForeignKey(User,null=True ,on_delete=models.CASCADE, verbose_name='Usuario que ejecuto el proceso')
    class Meta:
        db_table = 'PRCS_EJECUCION_PROCESO'