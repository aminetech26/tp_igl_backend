from rest_framework import serializers
from Articles.models import Article, Auteur
from Articles.serializers import AuteurSerializer, MotCleSerializer


class AuteurSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auteur
        fields = ["id", "nom", "prenom"]

class ArticleSearchResultSerializer(serializers.ModelSerializer):
    mot_cles = MotCleSerializer(many=True)
    auteurs = AuteurSearchResultSerializer(many=True)

    class Meta:
        model = Article
        fields = ["id", "titre","resume", "mot_cles", "auteurs"]