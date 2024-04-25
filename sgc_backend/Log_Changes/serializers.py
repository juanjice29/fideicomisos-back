from rest_framework import serializers
from .models import Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):   
   
    class Meta:
        model = User
        fields = ["id","username","first_name","last_name","email"]

class LogCreateSerializer(serializers.ModelSerializer):
    Usuario = UserSerializer(read_only=True) 
    class Meta:
        model = Log_Cambios_Create
        fields = '__all__'

class LogUpdateSerializer(serializers.ModelSerializer):
    Usuario = UserSerializer(read_only=True) 
    class Meta:
        model = Log_Cambios_Update
        fields = '__all__'

class LogDeleteSerializer(serializers.ModelSerializer):
    Usuario = UserSerializer(read_only=True) 
    class Meta:
        model = Log_Cambios_Delete
        fields = '__all__'