from rest_framework import serializers
from .models import Profile, Contact, LogBarImage

class LogBarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogBarImage
        fields = ['id', 'image', 'caption', 'order']


class ProfileSerializer(serializers.ModelSerializer):
    log_bar_images = serializers.SerializerMethodField()
    
    def get_log_bar_images(self, obj):
        request = self.context.get('request')
        if request:
            return [request.build_absolute_uri(image.image.url) for image in obj.log_bar_images.all()]
        return [image.image.url for image in obj.log_bar_images.all()]
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'name',
            'job_title',
            'job_description',
            'title',
            'description',
            'profile_picture',
            'secondary_picture',
            'log_bar_images'
        ]
        extra_kwargs = {
            'job_title': {'required': False},
            'job_description': {'required': False},
            'title': {'required': False},
            'description': {'required': False},
            'profile_picture': {'required': False},
            'secondary_picture': {'required': False},
        }


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'email',
            'phone',
            'address'
        ]