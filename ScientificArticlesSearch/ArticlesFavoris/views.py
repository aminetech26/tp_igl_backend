from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import ArticleFavoris
from .serializers import ArticleFavorisSerializer

class ArticleFavorisViewSet(viewsets.ModelViewSet):
    queryset = ArticleFavoris.objects.all()
    serializer_class = ArticleFavorisSerializer
    #permission_classes = [permissions.IsAuthenticated]
    
    
    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        queryset = ArticleFavoris.objects.filter(user=user_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        article_id = request.data.get('article_id')

        if ArticleFavoris.objects.filter(user=user_id,article=article_id).exists():
            return Response({'detail': 'article is already in favorites.'}, status=400)

        ArticleFavoris.objects.create(user=user_id,article=article_id)

        return Response({'detail': 'Article added to favorites successfully.'}, status=201)


    def destroy(self, request, *args, **kwargs):
        user_id = request.user.id
        article_id = kwargs.get('pk')

        try:
            article_favoris = ArticleFavoris.objects.get(user=user_id,article=article_id)
        except ArticleFavoris.DoesNotExist:
            return Response({'detail': 'Article not found in favorites.'}, status=404)

        article_favoris.delete()

        return Response({'detail': 'Article removed from favorites successfully.'}, status=204)
