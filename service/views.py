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
        title = request.query_params.get('title', None)
        if title:
            services = self.queryset.filter(title__iexact=title)
            types = Type.objects.filter(service__in=services).distinct()
            serializer = TypeSerializer(types, many=True)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(self.queryset, many=True)
            return Response(serializer.data)

class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
