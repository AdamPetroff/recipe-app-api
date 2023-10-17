from django.shortcuts import render
from rest_framework import generics, response, permissions, authentication
from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken import views
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class CreateTokenView(views.ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_object(self):
        return self.request.user

    # def get(self, request):
    #     user = request.user
    #     serializer = UserSerializer(user)
    #     return response.Response(serializer.data)
    # serializer_class = AuthTokenSerializer
    # renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
