from .models import Article,UploadedArticle
from .serializers import ArticleSerializer
from django.core.files.base import ContentFile
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .forms import ArticleUploadForm
import requests

class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    
    #TODO: override the create() method when pdf scrapper availlable 
    def create(self, request, *args, **kwargs):
        try:
            if(request.FILES.get('file') is not None):
                form = ArticleUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    #TODO: call pdf scrapper here
                    return Response({'message': 'Article uploaded successfully!'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
            elif request.data.get('url'):
                pdf_url = request.data['url'] 
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    file_content = ContentFile(response.content)
                    uploaded_article = UploadedArticle(file=file_content)
                    uploaded_article.save()
                    #TODO: call pdf scrapper here
                    return Response({'message': 'File downloaded and saved successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'message': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
                
            
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # extract article metadata
        # save article metadata to db
        # return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
