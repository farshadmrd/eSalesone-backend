from rest_framework import serializers
from .models import Profile, Contact


class ProfileSerializer(serializers.ModelSerializer):
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
            'secondary_picture'
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