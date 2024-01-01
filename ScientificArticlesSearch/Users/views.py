from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.conf import settings
from .utils import create_token, decode_token

TOKEN_EXPIRATION_ACCESS = 10
TOKEN_EXPIRATION_REFRESH = 1440


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # Model View Set already has the get() and get_by_id() create() and update() and delete() methods implemented
    
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