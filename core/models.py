from django.db import models
import uuid

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
    profile_picture = models.ImageField(upload_to='media/profile_pictures/', blank=True, null=True)
    secondary_picture = models.ImageField(upload_to='media/secondary_pictures/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
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