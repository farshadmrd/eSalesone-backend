from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Transaction
from .serializers import TransactionSerializer
from .email_service import TransactionEmailService
import logging

logger = logging.getLogger(__name__)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Transaction model providing CRUD operations.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new transaction with basket items.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Save the transaction
            transaction = serializer.save()
            
            # Send confirmation email
            try:
                email_service = TransactionEmailService()
                email_service.send_transaction_confirmation(transaction)
                logger.info(f"Confirmation email sent for transaction {transaction.id}")
            except Exception as e:
                logger.error(f"Failed to send confirmation email for transaction {transaction.id}: {str(e)}")
            
            # Return the created transaction with calculated amounts
            response_serializer = self.get_serializer(transaction)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """
        Process payment for a transaction.
        """
        transaction = self.get_object()
        
        if transaction.status != 'PENDING':
            return Response(
                {'error': 'Transaction has already been processed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simulate payment processing
        card_number = request.data.get('card_number', transaction.card_number)
        
        if card_number:
            # Simulate different payment outcomes based on card number
            if card_number == '1':  # ✅ Approved Transaction
                transaction.status = 'APPROVED'
                transaction.save()
                
                return Response({
                    'message': 'Payment approved successfully',
                    'transaction_id': transaction.id,
                    'status': transaction.status
                }, status=status.HTTP_200_OK)
                
            elif card_number == '2':  # ❌ Declined
                transaction.status = 'DECLINED'
                transaction.save()
                
                return Response({
                    'message': 'Payment declined',
                    'transaction_id': transaction.id,
                    'status': transaction.status
                }, status=status.HTTP_400_BAD_REQUEST)
            
            elif card_number == '3':  # ⚠️ Gateway Failure
                transaction.status = 'FAILED'
                transaction.save()
                
                return Response({
                    'message': 'Gateway failure - payment could not be processed',
                    'transaction_id': transaction.id,
                    'status': transaction.status
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            else:  # Default approved for other card numbers
                transaction.status = 'APPROVED'
                transaction.save()
                
                return Response({
                    'message': 'Payment approved successfully',
                    'transaction_id': transaction.id,
                    'status': transaction.status
                }, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Card number is required for payment processing'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Filter transactions by status.
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
        """
        email_param = request.query_params.get('email', None)
        if email_param:
            transactions = Transaction.objects.filter(email=email_param)
            serializer = self.get_serializer(transactions, many=True)
            return Response(serializer.data)
        return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
