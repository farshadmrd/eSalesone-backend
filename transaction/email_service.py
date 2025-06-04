"""
Email service for transaction notifications.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TransactionEmailService:
    """
    Service class to handle transaction-related email notifications.
    """
    
    @staticmethod
    def _get_basket_info(transaction):
        """
        Get comprehensive basket information for email templates.
        
        Args:
            transaction: Transaction instance
            
        Returns:
            dict: Basket information including services, totals, and counts
        """
        from service.models import Service, Type
        
        basket_info = {
            'services': [],
            'basket': {
                'total_amount': transaction.calculate_amount_from_basket(),
                'tax_amount': transaction.calculate_tax_amount(),
            },
            'total_amount': transaction.calculate_amount_from_basket(),
            'tax_amount': transaction.calculate_tax_amount(),
            'service_count': 0,
        }
        
        if transaction.basket:
            # Process each item in the JSON basket
            services_list = []
            unique_services = {}
            
            for item in transaction.basket:
                if 'service_type_id' in item and 'quantity' in item:
                    try:
                        service_type = Type.objects.select_related('service').get(id=item['service_type_id'])
                        service = service_type.service
                        quantity = int(item['quantity'])
                        
                        # Group by service and collect all types
                        if service.id not in unique_services:
                            unique_services[service.id] = {
                                'service': service,
                                'types': []
                            }
                        
                        # Add this type to the service
                        unique_services[service.id]['types'].append({
                            'type': service_type,
                            'quantity': quantity,
                            'subtotal': service_type.price * quantity
                        })
                        
                    except Type.DoesNotExist:
                        continue  # Skip invalid service types
            
            # Convert to list format for templates
            for service_data in unique_services.values():
                # Create a wrapper object that includes service data and types
                service = service_data['service']
                types_data = service_data['types']
                
                # Create a service wrapper with type information
                class ServiceWrapper:
                    def __init__(self, service, types_data):
                        # Django model managers and related fields to exclude
                        excluded_attrs = {
                            'objects', 'DoesNotExist', 'MultipleObjectsReturned', 'type_set',
                            '_meta', '_state', '_prefetched_objects_cache'
                        }
                        
                        # Copy safe attributes from the original service
                        for attr in dir(service):
                            if (not attr.startswith('_') and 
                                attr not in excluded_attrs and
                                not callable(getattr(service, attr, None)) and
                                not hasattr(getattr(service, attr, None), 'all')):  # Skip manager-like objects
                                try:
                                    setattr(self, attr, getattr(service, attr))
                                except (AttributeError, TypeError):
                                    continue  # Skip problematic attributes
                        
                        # Explicitly set essential service attributes
                        self.id = service.id
                        self.title = service.title  # Service model uses 'title', not 'name'
                        self.name = service.title   # Also set 'name' for template compatibility
                        self.description = getattr(service, 'description', '')
                        self.logo = getattr(service, 'logo', None)
                        
                        # Create type_set mock
                        self.type_set = MockTypeSet([t['type'] for t in types_data])
                        self.types_with_quantities = types_data
                
                # Create a simple mock object for type_set
                class MockTypeSet:
                    def __init__(self, types):
                        self._types = types
                    
                    def all(self):
                        return self._types
                
                service_wrapper = ServiceWrapper(service, types_data)
                services_list.append(service_wrapper)
            
            basket_info['services'] = services_list
            basket_info['service_count'] = len(services_list)
        
        return basket_info
    
    @staticmethod
    def send_transaction_approved_email(transaction):
        """
        Send an email notification for approved transactions.
        
        Args:
            transaction: Transaction instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Get comprehensive basket information
            basket_info = TransactionEmailService._get_basket_info(transaction)
            
            # Email context
            context = {
                'transaction': transaction,
                'services': basket_info['services'],
                'services_with_prices': basket_info.get('services_with_prices', []),
                'basket': basket_info['basket'],
                'basket_total': basket_info['total_amount'],
                'basket_tax': basket_info['tax_amount'],
                'service_count': basket_info['service_count'],
            }
            
            # Email subject
            subject = f'✅ Payment Approved - Order #{str(transaction.id)[:8]}... - eSalesOne'
            
            # Render email templates
            text_content = render_to_string('emails/transaction_approved.txt', context)
            html_content = render_to_string('emails/transaction_approved.html', context)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[transaction.email],
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            result = email.send()
            
            if result:
                logger.info(f"Approved transaction email sent successfully to {transaction.email} for transaction {transaction.id}")
                return True
            else:
                logger.error(f"Failed to send approved transaction email to {transaction.email} for transaction {transaction.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending approved transaction email to {transaction.email} for transaction {transaction.id}: {str(e)}")
            return False
    
    @staticmethod
    def send_transaction_failed_email(transaction):
        """
        Send an email notification for failed/declined transactions.
        
        Args:
            transaction: Transaction instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Get comprehensive basket information for failed transactions too
            basket_info = TransactionEmailService._get_basket_info(transaction)
            
            # Email context
            context = {
                'transaction': transaction,
                'services': basket_info['services'],
                'services_with_prices': basket_info.get('services_with_prices', []),
                'basket': basket_info['basket'],
                'basket_total': basket_info['total_amount'],
                'basket_tax': basket_info['tax_amount'],
                'service_count': basket_info['service_count'],
            }
            
            # Email subject
            subject = f'❌ Payment Failed - Order #{str(transaction.id)[:8]}... - eSalesOne'
            
            # Render email templates
            text_content = render_to_string('emails/transaction_failed.txt', context)
            html_content = render_to_string('emails/transaction_failed.html', context)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[transaction.email],
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            result = email.send()
            
            if result:
                logger.info(f"Failed transaction email sent successfully to {transaction.email} for transaction {transaction.id}")
                return True
            else:
                logger.error(f"Failed to send failed transaction email to {transaction.email} for transaction {transaction.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending failed transaction email to {transaction.email} for transaction {transaction.id}: {str(e)}")
            return False
    
    @staticmethod
    def send_transaction_notification(transaction):
        """
        Send appropriate email notification based on transaction status.
        
        Args:
            transaction: Transaction instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if transaction.status == 'APPROVED':
            return TransactionEmailService.send_transaction_approved_email(transaction)
        elif transaction.status in ['FAILED', 'DECLINED']:
            return TransactionEmailService.send_transaction_failed_email(transaction)
        else:
            logger.warning(f"No email template for transaction status: {transaction.status}")
            return False
