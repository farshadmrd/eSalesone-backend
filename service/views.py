from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Service, Type
from .serializers import ServiceSerializer, TypeSerializer

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        name = request.query_params.get('name', None)
        type = request.query_params.get('type', None)

        if name:
            queryset = queryset.filter(name__iexact=name)
        if type:
            queryset = queryset.filter(type__name__iexact=type)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
