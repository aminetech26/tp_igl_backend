from rest_framework import serializers
from articles.models import Article,Auteur
from articles.serializers import MotCleSerializer 

class AuteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auteur
        fields = ["id", "nom", "prenom"]

class ArticleSerializer(serializers.ModelSerializer):
    mot_cles = MotCleSerializer(many=True)
    auteurs = AuteurSerializer(many=True)

    class Meta:
        model = Article
        fields = ["id", "titre","resume", "mot_cles", "auteurs"]