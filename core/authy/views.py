from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt, datetime


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440),
            'iat': datetime.datetime.utcnow()
        }
        #refresh token will last for 24 hours
        RefreshToken = jwt.encode(payload, 'a-very-seCreT-kEy-WOW', algorithm='HS256')

        #access token
        #to test refresh i am putting the expiration time of the access token to 
        payload2 = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            'iat': datetime.datetime.utcnow()
        }       
        AccessToken = jwt.encode(payload2, 'a-very-seCreT-kEy-WOW', algorithm='HS256')
        response = Response()

        response.set_cookie(key='RefreshToken', value=RefreshToken, httponly=True)
        #user type is also returned in the response along with the access token
        response.data = {
            'AccessToken': AccessToken,
            'user-type' : user.user_type
        }
        return response



class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('AccessToken')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'a-very-seCreT-kEy-WOW', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

    
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('RefreshToken')
        response.data = {
            'message': 'success'
        }
        return response  

class RefreshView(APIView):
    def post(self, request):
        refreshToken = request.COOKIES.get('RefreshToken')
        if not refreshToken:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(refreshToken, 'a-very-seCreT-kEy-WOW', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!') 
        #generating a an access toen with the valid refresh token 
        id = payload['id']
        payload2 = {
            'id': id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }       
        AccessToken = jwt.encode(payload2, 'a-very-seCreT-kEy-WOW', algorithm='HS256') 
        response = Response()
        response.data = {
            'AccessToken': AccessToken,
            
        }
        return response
