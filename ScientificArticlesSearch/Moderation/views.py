from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from Users.models import User
from Users.serializers import UserSerializer
from django.core.mail import send_mail
from django.db import IntegrityError

class ModerationView(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(user_type='Mod')
    
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
            send_mail(
                'Account created',
                'Your account has been created successfully.',
                'settings.EMAIL_HOST_USER',
                [email],
                fail_silently=False,
            )
            return Response({'message': 'Moderator created successfully'}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'message': 'User with this email or username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
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
        
        
    def delete(self, request, *args, **kwargs):
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

