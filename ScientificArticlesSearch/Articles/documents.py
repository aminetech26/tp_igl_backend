from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Article


@registry.register_document
class ArticleDocument(Document):
    mot_cles = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "text": fields.TextField()
    }, multi=True)
    
    references_bibliographique = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "nom": fields.TextField()
    }, multi=True)
    
    auteurs = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "nom": fields.TextField(),
        "institutions": fields.ObjectField(properties={
            "id": fields.IntegerField(),
            "nom": fields.TextField(),
        }, multi=True)
    })

    date_de_publication = fields.DateField()

    class Index:
        name = "articles"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Article
        fields = [
            "id",
            "titre",
            "resume",
            "text_integral",
            "url",
        ]
