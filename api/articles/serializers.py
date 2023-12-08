from rest_framework import serializers
from .models import Article, MotCle, Institution, ReferenceBibliographique, Auteur


class MotCleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotCle
        fields = "__all__"


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = "__all__"


class ReferenceBibliographiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceBibliographique
        fields = "__all__"


class AuteurSerializer(serializers.ModelSerializer):
    institutions = InstitutionSerializer(many=True)

    class Meta:
        model = Auteur
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    mot_cles = MotCleSerializer(many=True)
    auteurs = AuteurSerializer(many=True)
    references_bibliographique = ReferenceBibliographiqueSerializer(many=True)

    class Meta:
        model = Article
        fields = "__all__"
