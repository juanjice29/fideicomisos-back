from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from django.contrib.auth import authenticate
from rest_framework import exceptions
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
                    msg = "User is deactivated."
                    raise exceptions.ValidationError(msg)
            else:
                msg = "Unable to login with provided credentials."
                raise exceptions.ValidationError(msg)
        else:
            msg = "Must provide username and password both."
            raise exceptions.ValidationError(msg)
        return data