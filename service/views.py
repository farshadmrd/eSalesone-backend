from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
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
            # Use prefetch_related to optimize the query for related types
            queryset = self.queryset.prefetch_related('type_set')
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class SessionBasketView(APIView):
    permission_classes = [AllowAny]
    
    def get_basket(self, request):
        """Get basket from session"""
        if 'basket' not in request.session:
            request.session['basket'] = {}
        return request.session['basket']
    
    def save_basket(self, request, basket):
        """Save basket to session"""
        request.session['basket'] = basket
        request.session.modified = True
    
    def get_basket_with_details(self, request):
        """Get basket with full service and type details"""
        basket = self.get_basket(request)
        detailed_basket = []
        total_amount = 0
        
        for key, item in basket.items():
            try:
                service = Service.objects.get(id=item['service_id'])
                service_type = Type.objects.get(id=item['service_type_id'])
                
                item_detail = {
                    'key': key,
                    'service': ServiceSerializer(service).data,
                    'service_type': TypeSerializer(service_type).data,
                    'quantity': item['quantity'],
                    'price': float(item['price']),
                    'subtotal': item['quantity'] * float(item['price'])
                }
                detailed_basket.append(item_detail)
                total_amount += item_detail['subtotal']
            except (Service.DoesNotExist, Type.DoesNotExist):
                continue
        
        return {
            'items': detailed_basket,
            'total_items': len(detailed_basket),
            'total_amount': total_amount
        }
    
    def get(self, request):
        """Get current basket"""
        basket_data = self.get_basket_with_details(request)
        return Response(basket_data)
    
    def post(self, request):
        """Add item to basket"""
        service_id = request.data.get('service_id')
        service_type_id = request.data.get('service_type_id')
        quantity = int(request.data.get('quantity', 1))
        price = float(request.data.get('price'))
        
        # Validate service and type exist
        try:
            service = Service.objects.get(id=service_id)
            service_type = Type.objects.get(id=service_type_id)
        except (Service.DoesNotExist, Type.DoesNotExist):
            return Response(
                {'error': 'Service or service type not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        basket = self.get_basket(request)
        item_key = f"{service_id}_{service_type_id}"
        
        if item_key in basket:
            # Update existing item
            basket[item_key]['quantity'] += quantity
        else:
            # Add new item
            basket[item_key] = {
                'service_id': service_id,
                'service_type_id': service_type_id,
                'quantity': quantity,
                'price': price
            }
        
        self.save_basket(request, basket)
        
        return Response({
            'message': 'Item added to basket successfully',
            'basket': self.get_basket_with_details(request)
        })
    
    def patch(self, request):
        """Update item quantity"""
        service_id = request.data.get('service_id')
        service_type_id = request.data.get('service_type_id')
        quantity = int(request.data.get('quantity', 1))
        
        basket = self.get_basket(request)
        item_key = f"{service_id}_{service_type_id}"
        
        if item_key not in basket:
            return Response(
                {'error': 'Item not found in basket'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            del basket[item_key]
        else:
            basket[item_key]['quantity'] = quantity
        
        self.save_basket(request, basket)
        
        return Response({
            'message': 'Item quantity updated successfully',
            'basket': self.get_basket_with_details(request)
        })
    
    def delete(self, request):
        """Remove item from basket"""
        service_id = request.data.get('service_id')
        service_type_id = request.data.get('service_type_id')
        
        basket = self.get_basket(request)
        item_key = f"{service_id}_{service_type_id}"
        
        if item_key not in basket:
            return Response(
                {'error': 'Item not found in basket'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        del basket[item_key]
        self.save_basket(request, basket)
        
        return Response({
            'message': 'Item removed from basket successfully',
            'basket': self.get_basket_with_details(request)
        })

@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_basket(request):
    """Clear entire basket"""
    request.session['basket'] = {}
    request.session.modified = True
    return Response({'message': 'Basket cleared successfully'})
