from rest_framework import serializers
from Articles.models import Article, Auteur, Institution

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ["id", "nom"]

class AuteurSearchResultSerializer(serializers.ModelSerializer):
    institutions = InstitutionSerializer(many=True)    
    class Meta:
        model = Auteur
        fields = ["id", "nom","institutions"]

class ArticleSearchResultSerializer(serializers.ModelSerializer):
    auteurs = AuteurSearchResultSerializer(many=True)

    class Meta:
        model = Article
        fields = ["id", "titre", "resume", "auteurs"]