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
    def send_transaction_approved_email(transaction):
        """
        Send an email notification for approved transactions.
        
        Args:
            transaction: Transaction instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Get services if basket exists
            services = []
            if transaction.basket:
                services = transaction.basket.services.all()
            
            # Email context
            context = {
                'transaction': transaction,
                'services': services,
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
            # Email context
            context = {
                'transaction': transaction,
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
        if transaction.status == 'COMPLETED':
            return TransactionEmailService.send_transaction_approved_email(transaction)
        elif transaction.status == 'FAILED':
            return TransactionEmailService.send_transaction_failed_email(transaction)
        else:
            logger.warning(f"No email template for transaction status: {transaction.status}")
            return False
