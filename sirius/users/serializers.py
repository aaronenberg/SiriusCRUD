from django.conf import settings
from rest_framework import serializers
from .models import BaseUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = (
            'email',
            'account_type',
            'password',
            'first_name',
            'middle_initial',
            'last_name',
            'date_joined',
            #'is_active',
            'is_staff',
            )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = BaseUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
