import datetime
from rest_framework import serializers
from .models import Fideicomiso

class FideicomisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fideicomiso
        fields = '__all__'