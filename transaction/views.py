from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Transaction, Basket
from .serializers import TransactionSerializer, BasketSerializer
from .email_service import TransactionEmailService
import logging

logger = logging.getLogger(__name__)


class BasketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Basket model providing CRUD operations.
    """
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    
    @action(detail=True, methods=['post'])
    def add_service(self, request, pk=None):
        """
        Add a service to the basket.
        """
        basket = self.get_object()
        service_id = request.data.get('service_id')
        
        if service_id:
            try:
                from service.models import Service
                service = Service.objects.get(id=service_id)
                basket.services.add(service)
                # Recalculate total amount if needed
                basket.save()
                return Response({'message': 'Service added to basket'}, status=status.HTTP_200_OK)
            except Service.DoesNotExist:
                return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'Service ID is required'}, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Transaction model providing CRUD operations.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Override create method to handle special card number logic.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the card number from validated data
        card_number = serializer.validated_data.get('card_number', '')
        clean_card = card_number.replace(' ', '').replace('-', '') if card_number else ''
        
        # Handle special test card numbers
        if clean_card == '1':
            # Approved transaction
            serializer.validated_data['status'] = 'COMPLETED'
        elif clean_card == '2':
            # Declined transaction
            serializer.validated_data['status'] = 'FAILED'
            serializer.validated_data['description'] = (
                serializer.validated_data.get('description', '') + 
                ' [Transaction Declined]'
            ).strip()
        elif clean_card == '3':
            # Gateway failure
            serializer.validated_data['status'] = 'FAILED'
            serializer.validated_data['description'] = (
                serializer.validated_data.get('description', '') + 
                ' [Gateway Failure]'
            ).strip()
        
        # Save the transaction
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Get the created transaction instance for email sending
        transaction = serializer.instance
        
        # Send email notification
        try:
            email_sent = TransactionEmailService.send_transaction_notification(transaction)
            if email_sent:
                logger.info(f"Email notification sent for transaction {transaction.id}")
            else:
                logger.warning(f"Failed to send email notification for transaction {transaction.id}")
        except Exception as e:
            logger.error(f"Error sending email for transaction {transaction.id}: {str(e)}")
        
        # Return appropriate response based on card number
        response_data = serializer.data.copy()
        
        if clean_card == '1':
            response_data['message'] = 'Transaction Approved'
        elif clean_card == '2':
            response_data['message'] = 'Transaction Declined'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST, headers=headers)
        elif clean_card == '3':
            response_data['message'] = 'Gateway Failure'
            return Response(response_data, status=status.HTTP_502_BAD_GATEWAY, headers=headers)
        else:
            response_data['message'] = 'Transaction created successfully'
        
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Filter transactions by status.
        Usage: /api/transactions/by_status/?status=COMPLETED
        """
        status_param = request.query_params.get('status', None)
        if status_param:
            transactions = Transaction.objects.filter(status=status_param)
            serializer = self.get_serializer(transactions, many=True)
            return Response(serializer.data)
        return Response({'error': 'Status parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Filter transactions by customer email.
        Usage: /api/transactions/by_customer/?email=customer@example.com
        """
        email_param = request.query_params.get('email', None)
        if email_param:
            transactions = Transaction.objects.filter(email=email_param)
            serializer = self.get_serializer(transactions, many=True)
            return Response(serializer.data)
        return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """
        Mark a transaction as completed.
        """
        transaction = self.get_object()
        transaction.status = 'COMPLETED'
        transaction.save()
        serializer = self.get_serializer(transaction)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def validate_payment(self, request):
        """
        Test payment validation without creating a transaction.
        Usage: POST /api/transactions/validate_payment/
        Body: {"card_number": "1", "expiry_date": "12/2025", "cvv": "123"}
        """
        card_number = request.data.get('card_number', '')
        expiry_date = request.data.get('expiry_date', '')
        cvv = request.data.get('cvv', '')
        
        # Use serializer validation
        serializer = self.get_serializer(data={
            'card_number': card_number,
            'expiry_date': expiry_date,
            'cvv': cvv,
            'full_name': 'Test',
            'email': 'test@example.com',
            'amount': '0.00'
        })
        
        try:
            serializer.is_valid(raise_exception=True)
            
            # Check card number behavior
            clean_card = card_number.replace(' ', '').replace('-', '') if card_number else ''
            
            if clean_card == '1':
                return Response({'message': '✅ Payment would be approved', 'status': 'approved'})
            elif clean_card == '2':
                return Response({'message': '❌ Payment would be declined', 'status': 'declined'})
            elif clean_card == '3':
                return Response({'message': '⚠️ Gateway failure would occur', 'status': 'gateway_failure'})
            else:
                return Response({'message': 'Payment validation passed', 'status': 'valid'})
                
        except serializers.ValidationError as e:
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def send_email_notification(self, request, pk=None):
        """
        Manually send email notification for a transaction.
        Usage: POST /api/transactions/{id}/send_email_notification/
        """
        transaction = self.get_object()
        
        try:
            email_sent = TransactionEmailService.send_transaction_notification(transaction)
            
            if email_sent:
                return Response({
                    'message': f'Email notification sent successfully to {transaction.email}',
                    'transaction_id': transaction.id,
                    'status': transaction.status
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to send email notification',
                    'transaction_id': transaction.id,
                    'status': transaction.status
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error manually sending email for transaction {transaction.id}: {str(e)}")
            return Response({
                'error': f'Error sending email: {str(e)}',
                'transaction_id': transaction.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
