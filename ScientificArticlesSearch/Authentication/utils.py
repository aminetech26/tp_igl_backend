import jwt
import datetime
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

def create_token(payload, expiration_minutes, secret_key=settings.SECRET_KEY):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes)
    payload['iat'] = datetime.datetime.utcnow()
    return jwt.encode(payload, secret_key, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')