from rest_framework import serializers
from .models import Service, Type

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    types = TypeSerializer(source='type_set', many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = '__all__'