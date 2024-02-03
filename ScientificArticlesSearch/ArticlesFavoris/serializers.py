from rest_framework import serializers
from .models import ArticleFavoris

class ArticleFavorisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleFavoris
        fields = "__all__"