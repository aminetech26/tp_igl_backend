from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from django.conf import settings
from .utils import create_token, decode_token
from rest_framework import status

from rest_framework.permissions import AllowAny, IsAuthenticated

TOKEN_EXPIRATION_ACCESS = 10
TOKEN_EXPIRATION_REFRESH = 1440


class AuthenticationViewSet(ViewSet):

    @action (detail=False, methods=['post'])
    def register(self, request):
        user_type = request.data.get('user_type')
        if user_type and user_type != 'User':
            return Response({'error': 'Only users with type "User" can register.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
    @action(detail=False, methods=['post'],permission_classes = (AllowAny,)) 
    def login(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        
        payload = {
            'id': user.id,
        }
        refresh_token = create_token(payload, TOKEN_EXPIRATION_REFRESH, settings.SECRET_KEY)
        access_token = create_token(payload, TOKEN_EXPIRATION_ACCESS, settings.SECRET_KEY)
        
        response = Response()

        response.set_cookie(key='RefreshToken', value=refresh_token, httponly=True)
        #user type is also returned in the response along with the access token
        response.data = {
            'AccessToken': access_token,
            'user-type' : user.user_type
        }
        return response
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        response = Response()
        response.delete_cookie('RefreshToken')
        response.data = {
            'message': 'success'
        }
        return response
    
    @action(detail=False, methods=['post'])
    def refresh(self,request):
        refresh_token = request.COOKIES.get('RefreshToken')
        if not refresh_token:
            raise AuthenticationFailed('Unauthenticated!')

        payload = decode_token(refresh_token)
        #generating a an access token with the valid refresh token 
        user_id = payload['id']
        payload = {
            'id': user_id,
        }       
        access_token = create_token(payload, TOKEN_EXPIRATION_ACCESS, settings.SECRET_KEY)
        response = Response()
        response.data = {
            'AccessToken': access_token,
        }
        return response