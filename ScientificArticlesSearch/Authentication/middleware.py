from django.conf import settings
import jwt
from .models import User


class AuthMiddleware :
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request ):
        authHeader = request.headers.get('Authorization')
        if not authHeader :
            request.auth = False
            return self.get_response(request)     
        access_token = authHeader.split(' ')[1]
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            
        except jwt.ExpiredSignatureError:
            print('token expired')
            return self.get_response(request)

        except jwt.InvalidTokenError:
            print('Invalid token')
            return self.get_response(request)
        request.user = User.objects.filter(id = payload['id']).first()
        request.Auth = True
        response = self.get_response(request)
        return response
       
    
               