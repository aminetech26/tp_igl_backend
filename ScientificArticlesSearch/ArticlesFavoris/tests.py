from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from Authentication.models import User
from ArticlesFavoris.models import ArticlesFavoris
from Articles.models import Article

class ArticlesFavorisApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            first_name="Khaled",
            last_name="BENMACHICHE",
            username="khaledbenmachiche",
            password="secure-password",
            email="lk_benmachiche@esi.dz",
        )
        
        cls.article1 = Article.objects.create(
            titre="Article 1",
            resume="Resume 1",
        )
        
        cls.article2 = Article.objects.create(
            titre="Article 2",
            resume="Resume 2",
        )
        ArticlesFavoris.objects.create(
            user=cls.user,
            article=cls.article1
        )
        ArticlesFavoris.objects.create(
            user=cls.user,
            article=cls.article2
        )
    
    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_get_favoris(self):
        url = reverse('favoris-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['titre'], 'Article 1')
        self.assertEqual(response.data[1]['titre'], 'Article 2')
    
    
    def test_add_favoris_successfully(self):
        url = reverse('favoris-list')
        new_article = Article.objects.create(
            titre="Article 3",
            resume="Resume 3",
        )
        data = {
            'article': new_article,
            'user': self.user
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArticlesFavoris.objects.count(), 3)
    
    def test_add_favoris_article_not_found(self):
        url = reverse('favoris-list')
        data = {
            'article': 100,
            'user': self.user
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ArticlesFavoris.objects.count(), 2)
        
    def test_add_favoris_article_deja_favoris(self):
        url = reverse('favoris-list')
        data = {
            'article': self.article1,
            'user': self.user
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ArticlesFavoris.objects.count(), 2)
    
    def test_add_favoris_article_not_validated(self):
        url = reverse('favoris-list')
        new_article = Article.objects.create(
            titre="Article 4",
            resume="Resume 4",
            is_validated=False
        )
        data = {
            'article': new_article,
            'user': self.user
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ArticlesFavoris.objects.count(), 2)
        
        
    def test_remove_favoris_successfully(self):
        url = reverse('favoris-detail', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ArticlesFavoris.objects.count(), 1)
    
    def test_remove_favoris_not_found(self):
        url = reverse('favoris-detail', kwargs={'pk': 100})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ArticlesFavoris.objects.count(), 2)