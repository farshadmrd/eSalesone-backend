import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_image_file_extension(value):
    """
    Validator for image files that accepts common image formats including SVG.
    """
    allowed_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', 
        '.webp', '.svg', '.ico'
    ]
    
    if value:
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                _('Unsupported file extension. Allowed extensions are: %(allowed_extensions)s'),
                params={'allowed_extensions': ', '.join(allowed_extensions)},
                code='invalid_extension'
            )

def validate_logo_file_extension(value):
    """
    Validator specifically for logo files (includes SVG for scalable logos).
    """
    allowed_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico'
    ]
    
    if value:
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                _('Unsupported logo file extension. Allowed extensions are: %(allowed_extensions)s'),
                params={'allowed_extensions': ', '.join(allowed_extensions)},
                code='invalid_extension'
            )
