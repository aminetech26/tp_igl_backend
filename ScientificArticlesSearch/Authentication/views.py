from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from django.conf import settings
from .utils import create_token, decode_token
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

TOKEN_EXPIRATION_ACCESS = 600
TOKEN_EXPIRATION_REFRESH = 1440


class AuthenticationViewSet(ViewSet):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='User username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='User first name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='User last name'),
            },
            required=['username', 'password'],
        ),
        operation_description="Register a user",
        responses={
            201: openapi.Response('User registered', UserSerializer),
            400: openapi.Response('Bad request'),
        }
    )
    @action (detail=False, methods=['post'])
    def register(self, request):
        user_type = request.data.get('user_type')
        if user_type and user_type != 'User':
            return Response({'error': 'Only users with type "User" can register.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='User username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            },
            required=['username', 'password'],
        ),
        operation_description="Login a user",
        responses={
            200: openapi.Response('User logged in', openapi.Schema(type=openapi.TYPE_OBJECT,properties={'username': openapi.Schema(type=openapi.TYPE_STRING, description='User username'),'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),},required=['username', 'password'])),
            400: openapi.Response('Bad request'),
        }
    )
    @action(detail=False, methods=['post'])
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