from rest_framework import serializers
from .models import User, InvitationCode


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class InvitationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationCode
        fields = '__all__'
