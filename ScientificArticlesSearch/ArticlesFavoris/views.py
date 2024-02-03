from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import ArticleFavoris
from .serializers import ArticleFavorisSerializer
from Articles.models import Article
from Authentication.models import User
from .CustomPermissions import IsAuth,IsAdmin,IsModerator
from rest_framework.permissions import AllowAny , IsAuthenticated
from Articles.serializers import ArticleSerializer
class ArticleFavorisViewSet(viewsets.ModelViewSet):
    queryset = ArticleFavoris.objects.all()
    serializer_class = ArticleFavorisSerializer
    permission_classes = [IsAuthenticated]
    
    
    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        favorite_articles = ArticleFavoris.objects.filter(user=user_id)
        articles = [fav.article for fav in favorite_articles]
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        if not user:
            return Response({'detail': 'User not found.'}, status=404)
        if user.user_type != 'User':
            return Response({'detail': 'Only users can add articles to favorites.'}, status=400)
        
        
        article_id =  request.data.get('article_id')
        article = Article.objects.get(id=article_id)
        if not article:
            return Response({'detail': 'Article not found.'}, status=404)
        if not article.is_validated:
            return Response({'detail': 'Article is not validated.'}, status=400)
        
        
        if ArticleFavoris.objects.filter(user=user,article=article).exists():
            return Response({'detail': 'article is already in favorites.'}, status=400)

        ArticleFavoris.objects.create(user=user,article=article)

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
