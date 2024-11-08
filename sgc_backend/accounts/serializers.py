from logging import Logger
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import *
from collections import defaultdict
from django.contrib.auth import authenticate
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['rol'] = user.profile.rol.nombre # Add the role to the token
        try:
            token['rol'] = user.profile.rol.nombre # Add the role to the token
        except AttributeError as e:
            Logger.error('Error al obtener el rol: %s', str(e))
    
        return token
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add the user to the validated data
        data['user'] = self.user

        return data
    
class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user login.

    This serializer accepts a username and password and validates them.
    """
    class Meta:
        model = Profile
        fields = '__all__' 
        
class LoginSerializer(serializers.Serializer):
    """
        Validate the username and password.

        If the username and password are valid and the user is active, the user is authenticated.
        If the username and password are not valid or the user is not active, a ValidationError is raised.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        username = data.get("username", "")
        password = data.get("password", "")

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    msg = "El usuario esta desactivado."
                    raise exceptions.ValidationError(msg)
            else:
                msg = "No fue posible ingresar con las credenciales brindadas."
                raise exceptions.ValidationError(msg)
        else:
            msg = "Debe ingresar nombre de usuario y contraseña."
            raise exceptions.ValidationError(msg)
        return data

class UserSerializer(serializers.ModelSerializer):  
   
    class Meta:
        model = User
        fields = ["id","username","first_name","last_name","email"]
        ref_name = 'AccountsUserSerializer'
        
class PermisosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permisos
        fields = ['rol', 'vista', 'accion']

class PantallaSerializer(serializers.ModelSerializer):
    permisos = PermisosSerializer(many=True, read_only=True)

    class Meta:
        model = Pantalla
        fields = ['nombre', 'url', 'descripcion', 'permisos']

class PantallaPermisosSerializer(serializers.ModelSerializer):
    pantalla = PantallaSerializer()
    permiso = PermisosSerializer()

    class Meta:
        model = PantallaPermisos
        fields = ['pantalla', 'permiso']