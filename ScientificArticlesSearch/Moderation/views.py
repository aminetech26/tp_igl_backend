from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from Authentication.models import User
from Authentication.serializers import UserSerializer

from .CustomPermissions import IsAdmin,IsModerator
from rest_framework.permissions import AllowAny , IsAuthenticated

from django.db import IntegrityError
from .utils import send_moderator_account_create_email
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
class ModerationView(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(user_type='Mod')
    permission_classes = (IsAuthenticated,IsAdmin,)
    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        user_type = 'Mod'
        
        if not email or not username or not password or not first_name or not last_name:
            return Response({'message': 'Please provide all the required fields.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=user_type)
            user.save()
            send_moderator_account_create_email(username, email, first_name, last_name)
            
            return Response({'message': 'Moderator created successfully'}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'message': 'User with this username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def update(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.email = request.data.get('email', user.email)
            user.username = request.data.get('username', user.username)
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            user.save()
            return Response({'message': 'Moderator updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Moderator not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'moderators_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description='List of moderators ids'),
            },
            required=['moderators_ids'],
        ),
        operation_description="delete moderateurs by ids",
        responses={
            204: openapi.Response('moderateurs deleted successfully', UserSerializer),
            400: openapi.Response('Bad request, Please provide moderators ids.'),
            404: openapi.Response('No moderators found'),
            500: openapi.Response('Internal server error'),
        }
    )
    @action(detail=False, methods=['delete'])
    def delete_by_ids(self, request, *args, **kwargs):
        moderators_ids = request.data.get('moderators_ids')
        if not moderators_ids:
            return Response({'message': 'Please provide moderators ids.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            moderators = self.get_queryset().filter(id__in=moderators_ids)
            if not moderators.exists():
                return Response({'message': 'No moderators found.'}, status=status.HTTP_404_NOT_FOUND)
            
            moderators.delete()
            return Response({'message': 'Moderators deleted successfully'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'message': 'No moderators found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

