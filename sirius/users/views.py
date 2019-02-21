from django.shortcuts import render
from django.contrib.auth import login, authenticate
from rest_framework import generics
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import UserSerializer
from .models import BaseUser

class SignUpView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = BaseUser.objects.all()
    serializer_class = UserSerializer

    #def post(self, request, *args, **kwargs):

