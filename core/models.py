from django.db import models
import uuid
from .validators import validate_image_file_extension

class Profile(models.Model):
    """
    Represents a user profile with personal and professional details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    job_description = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    profile_picture = models.FileField(upload_to='media/profile_pictures/', blank=True, null=True)
    secondary_picture = models.FileField(upload_to='media/secondary_pictures/', blank=True, null=True)
    def __str__(self):
        return self.name


class LogBarImage(models.Model):
    """
    Represents images for the log bar of a profile.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='log_bar_images')
    image = models.FileField(upload_to='media/log_bar_images/')
    caption = models.FileField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of the image in the log bar")
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Log bar image for {self.profile.name}"
    
class Contact(models.Model):
    """
    Represents contact information for a user profile.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    def __str__(self):
        return self.email