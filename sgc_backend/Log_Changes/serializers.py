from rest_framework import serializers
from .models import Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete

class LogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Cambios_Create
        fields = '__all__'

class LogUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Cambios_Update
        fields = '__all__'

class LogDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Cambios_Delete
        fields = '__all__'