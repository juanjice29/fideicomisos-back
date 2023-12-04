from tokenize import TokenError
from .serializers import LoginSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import serializers
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import Permisos
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Role, View, Permisos
@permission_classes([AllowAny])
class LoginView(APIView):
    serializer_class = MyTokenObtainPairSerializer
    """
    This view handles user login.

    It uses the Django REST Framework's APIView class to handle requests.
    """
    """
    post:
    Authenticate a user and return a refresh and an access token.
    """
    @swagger_auto_schema(
        operation_description="Ingreso de usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Usuario'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='contraseña'),
            },
        ),
        responses={200: openapi.Response('Ingresado Exitosamente', LoginSerializer)},
    )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Check if the user is active
        user = serializer.validated_data['user']
        if not user.is_active:
            return Response({"detail": "Account is inactive"}, status=400)

        data = serializer.validated_data

        # Fetch the views that the user's role has permission to access
        views = list(Permisos.objects.filter(role__name=user.profile.rol.name).values_list('view__name', flat=True))

        response_data = {
            'user': {
                'username': user.username,
                'rol': user.profile.rol.name,
                'views': views,  # Add the views to the response data
            },
            'access': data['access'],
            'refresh': data['refresh'],
        }

        return Response(response_data)