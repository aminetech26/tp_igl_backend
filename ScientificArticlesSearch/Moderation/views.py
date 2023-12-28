from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from Users.models import User
from Users.models import UserSerializer


class ModerationView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            users = User.objects.filter(user_type='Mod')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def post(self, request, *args, **kwargs):
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
            return Response({'message': 'Moderator created successfully'}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.data['id'])
            user.email = request.data['email']
            user.username = request.data['username']
            user.first_name = request.data['first_name']
            user.last_name = request.data['last_name']
            user.save()
            return Response({'message': 'Moderator updated successfully'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, *args, **kwargs):
        moderators_ids = request.data.get('moderators_ids')
        if not moderators_ids:
            return Response({'message': 'Please provide moderators ids.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            moderators = User.objects.filter(id__in=moderators_ids, user_type='Mod')
            if not moderators.exists():
                return Response({'message': 'No moderators found.'}, status=status.HTTP_404_NOT_FOUND)
            
            moderators.delete()
            return Response({'message': 'Moderators deleted successfully'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
