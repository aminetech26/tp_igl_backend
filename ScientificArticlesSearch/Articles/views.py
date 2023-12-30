from django.core.files.base import ContentFile

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from .forms import ArticleUploadForm
from .models import Article,UploadedArticle
from .serializers import ArticleSerializer
from zipfile import ZipFile
import requests
from .scrapping.scrapping_manager import ScrappingManager
from django.conf import settings
from django.core.files.storage import FileSystemStorage
class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    
    @action(detail=False, methods=['post'], url_path='upload-via-file')
    def upload_article_via_file(self, request, *args, **kwargs):
        try:
            if(request.FILES.get('file') is not None):
                form = ArticleUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    #TODO: call pdf scrapper here
                    return Response({'message': 'Article uploaded successfully!'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='upload-via-zip')
    def upload_article_via_zip(self, request, *args, **kwargs):
        try:
            zip_file = request.FILES.get('file')
            if not zip_file.name.endswith('.zip'):
                return Response({'message': 'Please upload a zip file.'}, status=status.HTTP_400_BAD_REQUEST)
            
            with ZipFile(zip_file,'r') as zip:
                pdf_files = [file for file in zip.filelist if file.filename.lower().endswith('.pdf')]
                if not pdf_files:
                    return Response({'message': 'No PDF files found in the zip file.'}, status=status.HTTP_400_BAD_REQUEST)
                
                fs = FileSystemStorage()
                for file in zip.filelist:
                    if file.filename.lower().endswith('.pdf'):
                        file_name = file.filename.split('/')[-1]
                        file_content = ContentFile(zip.read(file))
                        file_name = fs.save(file_name, file_content)
                        file_path = fs.url(file_name)
                        uploaded_article = UploadedArticle(file=file_path.lstrip('/'))
                        uploaded_article.save()
                        #TODO: call pdf scrapper here for each file
            
            return Response({'message': 'Articles uploaded successfully'}, status=status.HTTP_201_CREATED)
                
        except Exception:
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    
    @action(detail=False, methods=['post'], url_path='upload-via-url')
    def upload_article_via_url(self, request, *args, **kwargs):
        try:
            if request.data.get('url'):
                    pdf_url = request.data['url']
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        file_name = pdf_url.split('/')[-1]
                        file_content = ContentFile(response.content)
                        fs = FileSystemStorage()
                        file_name = fs.save(file_name, file_content)
                        file_path = fs.url(file_name)
                        uploaded_article = UploadedArticle(file=file_path.lstrip('/'))
                        uploaded_article.save()
                        #TODO: call pdf scrapper here
                        return Response({'message': 'File downloaded and saved successfully'}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message': 'Please provide a url'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(e)
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='upload-via-drive')
    def upload_article_via_drive(self, request, *args, **kwargs):
        try:
            scrapper = ScrappingManager()
            scrapper.run_scrapper()
            return Response({'message': 'File downloaded and saved successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'message': "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
