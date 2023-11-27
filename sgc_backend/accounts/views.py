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
@permission_classes([AllowAny])
class LoginView(APIView):
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
    def post(self, request):
        """
        Handle POST requests.

        This method authenticates the user and returns a refresh and an access token.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)