from django.db import models


class ReferenceBibliographique(models.Model):
    nom = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MotCle(models.Model):
    text = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Institution(models.Model):
    nom = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Auteur(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    institutions = models.ManyToManyField(Institution)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Article(models.Model):
    titre = models.CharField(max_length=200)
    resume = models.CharField(max_length=2000)
    text_integral = models.CharField(max_length=10000)
    url = models.CharField(max_length=100)
    date_de_publication = models.DateField()
    mot_cles = models.ManyToManyField(MotCle)
    auteurs = models.ManyToManyField(Auteur)
    references_bibliographique = models.ManyToManyField(ReferenceBibliographique)
    is_validated=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UploadedArticle(models.Model):
    file = models.FileField(upload_to='./')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)