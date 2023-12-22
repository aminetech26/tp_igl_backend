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
    
    def create(self, validated_data):
        mot_cles = validated_data.pop('mot_cles',[])
        auteurs = validated_data.pop('auteurs',[])
        references_bibliographique = validated_data.pop('references_bibliographique',[])
        article_instance = Article.objects.create(**validated_data)
        for mot_cle in mot_cles:
            mot_cle_instance = MotCle.objects.create(**mot_cle,article=article_instance)
            article_instance.mot_cles.add(mot_cle_instance)
            
        for auteur in auteurs:
            institutions = auteur.pop('institutions',[])
            auteur_instance = Auteur.objects.create(**auteur,article=article_instance)
            for institution in institutions:
                institution_instance = Institution.objects.create(**institution,auteur=auteur_instance)
                auteur_instance.institutions.add(institution_instance)
            article_instance.auteurs.add(auteur_instance)
        
        for reference_bibliographique in references_bibliographique:
            reference_bibliographique_instance = ReferenceBibliographique.objects.create(**reference_bibliographique,article=article_instance)
            article_instance.references_bibliographique.add(reference_bibliographique_instance)
        article_instance.save()
        return article_instance
    
    def update(self, instance, validated_data):
        mot_cles = validated_data.pop('mot_cles',[])
        auteurs = validated_data.pop('auteurs',[])
        references_bibliographique = validated_data.pop('references_bibliographique',[])
        instance.titre = validated_data.get('titre',instance.titre)
        instance.resume = validated_data.get('resume',instance.resume)
        instance.text_integral = validated_data.get('text_integral',instance.text_integral)
        instance.url = validated_data.get('url',instance.url)
        instance.date_de_publication = validated_data.get('date_de_publication',instance.date_de_publication)
        instance.save()
        
        for mot_cle in mot_cles:
            mot_cle_instance = MotCle.objects.create(**mot_cle,article=instance)
            instance.mot_cles.add(mot_cle_instance)
            
        for auteur in auteurs:
            institutions = auteur.pop('institutions',[])
            auteur_instance = Auteur.objects.create(**auteur,article=instance)
            for institution in institutions:
                institution_instance = Institution.objects.create(**institution,auteur=auteur_instance)
                auteur_instance.institutions.add(institution_instance)
            instance.auteurs.add(auteur_instance)
        
        for reference_bibliographique in references_bibliographique:
            reference_bibliographique_instance = ReferenceBibliographique.objects.create(**reference_bibliographique,article=instance)
            instance.references_bibliographique.add(reference_bibliographique_instance)
        instance.save()
        return instance
    