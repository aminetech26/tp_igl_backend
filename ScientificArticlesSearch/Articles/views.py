from .models import Article
from .serializers import ArticleSerializer
from rest_framework.viewsets import ModelViewSet

class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    
    #TODO: override the create() method when pdf scrapper availlable 
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
