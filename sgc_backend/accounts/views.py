from tokenize import TokenError
from .serializers import LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.status import HTTP_403_FORBIDDEN
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from .serializers import MyTokenObtainPairSerializer, PantallaPermisosSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import Permisos, PantallaPermisos
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import  Permisos
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from collections import defaultdict
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User

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
        
        try:
            serializer = self.serializer_class(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except TokenError as e:
                raise InvalidToken(e.args[0])

            # Check if the user is active
            user = serializer.validated_data['user']
            if not user.is_active:
                return Response({"detail": "Cuenta Inactiva"}, status=400)

            data = serializer.validated_data

            # Fetch the views that the user's role has permission to access
            views = list(Permisos.objects.filter(rol__nombre=user.profile.rol.nombre).values_list('vista__nombre', flat=True))
            user.last_login = timezone.now()
            user.save()
            response_data = {
                'user': {
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'email': user.email,
                    'username': user.username,
                    'rol': user.profile.rol.nombre,
                    'dni':user.profile.cedula,
                    'lastLogin': user.last_login,
                },
                'access': data['access'],
                'refresh': data['refresh'],
            }

            return Response(response_data)
        except AuthenticationFailed as e:
                return Response({'error': 'Credenciales invalidas'}, status=HTTP_403_FORBIDDEN)
class PermisosView(APIView):
    def get(self, request):
        pantalla_permisos = PantallaPermisos.objects.all()
        serializer = PantallaPermisosSerializer(pantalla_permisos, many=True)
        return Response(serializer.data)
class PasswordResetView(APIView):
    """
    post:
    Send a password reset email to the user.
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        form = PasswordResetForm(data={'email': user.email})
        if form.is_valid():
            form.save(
                use_https=request.is_secure(),
                email_template_name='password_reset_email.html',
                request=request,
            )
            return Response({"detail": "Password reset email has been sent."})
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """
    post:
    Reset the user's password.
    """
    def post(self, request, *args, **kwargs):
        uidb64 = kwargs['uidb64']
        token = kwargs['token']

        try:
            uid = uid_decoder(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user, request.data)
            if form.is_valid():
                form.save()
                return Response({"detail": "Password has been reset."})
            else:
                return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Password reset unsuccessful."}, status=status.HTTP_400_BAD_REQUEST)