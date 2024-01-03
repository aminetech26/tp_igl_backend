from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from Users.models import User
from Users.serializers import UserSerializer
from django.core.mail import send_mail
from django.db import IntegrityError
from django.conf import settings
class ModerationView(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(user_type='Mod')
    
    
    def create(self, request, *args, **kwargs):
        users_id = request.data.get('users_ids',[])
        if not users_id:
            return Response({'message': 'Please provide moderators ids.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            for user_id in users_id:
                existing_user = User.objects.get(id=user_id)
                
                new_moderator = User.objects.create(
                    email=existing_user.email,
                    username=f"{existing_user.username}_moderateur",
                    first_name=existing_user.first_name,
                    last_name=existing_user.last_name,
                    password=existing_user.password,
                    user_type='Mod'
                )
                new_moderator.save()
                send_mail(
                    'Moderator account created',
                    'You have been added as a moderator.',
                    settings.EMAIL_HOST_USER,
                    [existing_user.email],
                    fail_silently=False,
                )
            return Response({'message': 'Moderator added successfully'}, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
                return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
                return Response({'message': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
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

