from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Article,Auteur,Institution,MotCle,ReferenceBibliographique
from .serializers import ArticleSerializer

class InstitutionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.institution = Institution.objects.create(nom="ESI")
        
    def test_institution_content(self):
        self.assertEquals(self.institution.nom,'ESI')
        

class MotCleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.motcle = MotCle.objects.create(text="Graph Coloring Problem")
        
    def test_motcle_content(self):
        self.assertEquals(self.motcle.text,'Graph Coloring Problem')


class ReferenceBibliographiqueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.referencebibliographique = ReferenceBibliographique.objects.create(nom="International Conference on New Trends in Computing Sciences (ICTCS)")
        
    def test_referencebibliographique_content(self):
        self.assertEquals(self.referencebibliographique.nom,'International Conference on New Trends in Computing Sciences (ICTCS)')
        
class AuteurTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        institution = Institution.objects.create(nom="ESI")
        
        cls.auteur = Auteur.objects.create(nom="Yessed",prenom="Lamia")
        cls.auteur.institutions.set([institution])
        
    def test_auteur_content(self):
        self.assertEquals(self.auteur.nom,'Yessed')
        self.assertEquals(self.auteur.prenom,'Lamia')
        self.assertEquals(self.auteur.institutions.first().nom,'ESI')
        
class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        institution = Institution.objects.create(nom="ESI")
        motcle = MotCle.objects.create(text="Graph Coloring Problem")
        referencebibliographique = ReferenceBibliographique.objects.create(nom="International Conference on New Trends in Computing Sciences (ICTCS)")
        auteur = Auteur.objects.create(nom="Yessed",prenom="Lamia")
        auteur.institutions.set([institution])
        
        cls.article = Article.objects.create(titre="titre",resume="resume",text_integral="text_integral",url="url",date_de_publication="2021-01-01")
        cls.article.mot_cles.set([motcle])
        cls.article.auteurs.set([auteur])
        cls.article.references_bibliographique.set([referencebibliographique])
        
    def test_article_content(self):
        self.assertEquals(self.article.titre,'titre')
        self.assertEquals(self.article.resume,'resume')
        self.assertEquals(self.article.text_integral,'text_integral')
        self.assertEquals(self.article.url,'url')
        self.assertEquals(self.article.date_de_publication,'2021-01-01')
        self.assertEquals(self.article.mot_cles.first().text,'Graph Coloring Problem')
        self.assertEquals(self.article.auteurs.first().nom,'Yessed')
        self.assertEquals(self.article.auteurs.first().prenom,'Lamia')
        self.assertEquals(self.article.auteurs.first().institutions.first().nom,'ESI')
        self.assertEquals(self.article.references_bibliographique.first().nom,'International Conference on New Trends in Computing Sciences (ICTCS)')
        

class ArticleApiTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        institution = Institution.objects.create(nom="nom")
        motcle = MotCle.objects.create(text="text")
        referencebibliographique = ReferenceBibliographique.objects.create(nom="nom")
        auteur = Auteur.objects.create(nom="nom",prenom="prenom")
        auteur.institutions.set([institution])
        
        cls.article = Article.objects.create(
            titre="titre",
            resume="resume",
            text_integral="text_integral",
            url="url",
            date_de_publication="2021-01-01"
        )
        cls.article.mot_cles.set([motcle])
        cls.article.auteurs.set([auteur])
        cls.article.references_bibliographique.set([referencebibliographique])
    
    def setUp(self) -> None:
        self.client = APIClient()
    
    def test_get_all_articles(self):
        url = reverse('article-list')
        response = self.client.get(url)
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(response.data.get('results'), serializer.data)
        self.assertEqual(response.data.get('count'), len(serializer.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_post_article(self):
        url = reverse('article-list')
        data = {
            "titre": "titre",
            "resume": "resume",
            "text_integral": "text_integral",
            "url": "url",
            "date_de_publication": "2021-01-01",
            "mot_cles": [
                {
                    "text": "text"
                }
            ],
            "auteurs": [
                {
                    "nom": "nom",
                    "prenom": "prenom",
                    "institutions": [
                        {
                            "nom": "nom",
                        }
                    ]
                }
            ],
            "references_bibliographique": [
                {
                    "nom": "nom"
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(Article.objects.last().titre, 'titre')
        self.assertEqual(Article.objects.last().resume, 'resume')
        self.assertEqual(Article.objects.last().text_integral, 'text_integral')
        self.assertEqual(Article.objects.last().url, 'url')
        self.assertEqual(Article.objects.last().date_de_publication.__str__(), '2021-01-01')
        self.assertEqual(Article.objects.last().mot_cles.first().text, 'text')
        self.assertEqual(Article.objects.last().auteurs.first().nom, 'nom')
        self.assertEqual(Article.objects.last().auteurs.first().prenom, 'prenom')
        self.assertEqual(Article.objects.last().auteurs.first().institutions.first().nom, 'nom')
        self.assertEqual(Article.objects.last().references_bibliographique.first().nom, 'nom')
    
    def test_post_article_with_empty_data(self):
        url = reverse('article-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_post_article_with_invalid_data(self):
        url = reverse('article-list')
        data = {
            "title": "titre", # valid field is titre not title
            "resume": "resume",
            "text_integral": "text_integral",
            "url": "url",
            "date_de_publication": "2021-01-01",
            "mot_cles": [
                {
                    "text": "text"
                }
            ],
            "auteurs": [
                {
                    "nom": "nom",
                    "prenom": "prenom",
                    "institutions": [
                        {
                            "nom": "nom",
                        }
                    ]
                }
            ],
            "references_bibliographique": [
                {
                    "nom": "nom"
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(MotCle.objects.count(), 1)
        self.assertEqual(Auteur.objects.count(), 1)
        self.assertEqual(Institution.objects.count(), 1)
        self.assertEqual(ReferenceBibliographique.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_article(self):
        url = reverse('article-detail', args=[self.article.id])
        response = self.client.get(url)
        serializer = ArticleSerializer(self.article)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_article_not_found(self):
        url = reverse('article-detail', args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_article(self):
        url = reverse('article-detail', args=[self.article.id])
        data = {
            "titre": "titre",
            "resume": "resume",
            "text_integral": "text_integral",
            "url": "url",
            "date_de_publication": "2021-01-01",
            "mot_cles": [
                {
                    "text": "text"
                }
            ],
            "auteurs": [
                {
                    "nom": "nom",
                    "prenom": "prenom",
                    "institutions": [
                        {
                            "nom": "nom",
                        }
                    ]
                }
            ],
            "references_bibliographique": [
                {
                    "nom": "nom"
                }
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(Article.objects.last().titre, 'titre')
        self.assertEqual(Article.objects.last().resume, 'resume')
        self.assertEqual(Article.objects.last().text_integral, 'text_integral')
        self.assertEqual(Article.objects.last().url, 'url')
        self.assertEqual(Article.objects.last().date_de_publication.__str__(), '2021-01-01')
        self.assertEqual(Article.objects.last().mot_cles.first().text, 'text')
        self.assertEqual(Article.objects.last().auteurs.first().nom, 'nom')
        self.assertEqual(Article.objects.last().auteurs.first().prenom, 'prenom')
        self.assertEqual(Article.objects.last().auteurs.first().institutions.first().nom, 'nom')
        self.assertEqual(Article.objects.last().references_bibliographique.first().nom, 'nom')
        
        
    def test_put_article_not_found(self):
        url = reverse('article-detail', args=[100])
        data = {
            "titre": "titre",
            "resume": "resume",
            "text_integral": "text_integral",
            "url": "url",
            "date_de_publication": "2021-01-01",
            "mot_cles": [
                {
                    "text": "text"
                }
            ],
            "auteurs": [
                {
                    "nom": "nom",
                    "prenom": "prenom",
                    "institutions": [
                        {
                            "nom": "nom",
                        }
                    ]
                }
            ],
            "references_bibliographique": [
                {
                    "nom": "nom"
                }
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_article_with_empty_data(self):
        url = reverse('article-detail', args=[self.article.id])
        data = {}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_put_article_with_invalid_data(self):
        url = reverse('article-detail', args=[self.article.id])
        data = {
            "title": "titre", # valid field is titre not title
            "resume": "resume",
            "text_integral": "text_integral",
            "url": "url",
            "date_de_publication": "2021-01-01",
            "mot_cles": [
                {
                    "text": "text"
                }
            ],
            "auteurs": [
                {
                    "nom": "nom",
                    "prenom": "prenom",
                    "institutions": [
                        {
                            "nom": "nom",
                        }
                    ]
                }
            ],
            "references_bibliographique": [
                {
                    "nom": "nom"
                }
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(MotCle.objects.count(), 1)
        self.assertEqual(Auteur.objects.count(), 1)
        self.assertEqual(Institution.objects.count(), 1)
        self.assertEqual(ReferenceBibliographique.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_delete_article(self):
        url = reverse('article-detail', args=[self.article.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 0)
        self.assertEqual(MotCle.objects.count(), 1)
        self.assertEqual(Auteur.objects.count(), 1)
        self.assertEqual(Institution.objects.count(), 1)
        self.assertEqual(ReferenceBibliographique.objects.count(), 1)
    
    def test_delete_article_not_found(self):
        url = reverse('article-detail', args=[100])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(MotCle.objects.count(), 1)
        self.assertEqual(Auteur.objects.count(), 1)
        self.assertEqual(Institution.objects.count(), 1)
        self.assertEqual(ReferenceBibliographique.objects.count(), 1)
    