import abc

from django.http import HttpResponse
from elasticsearch_dsl import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from articles.documents import ArticleDocument
from .serializers import ArticleSerializer


class PaginatedElasticSearchAPIView(APIView, LimitOffsetPagination):
    serializer_class = None
    document_class = None

    @abc.abstractmethod
    def generate_q_expression(self, query, filters):
        """This method should be overridden
        and return a Q() expression."""

    def get(self, request, query):
        try:
            filters = request.GET.dict()
            q = self.generate_q_expression(query, filters)

            search = self.document_class.search().query(q)
            response = search.execute()

            print(f'Found {response.hits.total.value} hit(s) for query: "{query}"')

            results = self.paginate_queryset(response, request, view=self)
            serializer = self.serializer_class(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return HttpResponse(e, status=500)


class SearchArticles(PaginatedElasticSearchAPIView):
    serializer_class = ArticleSerializer
    document_class = ArticleDocument

    def generate_q_expression(self, query, filters=None):
        return Q(
            "multi_match",
            query=query,
            type="most_fields",
            fields=[
                "titre",
                "text_integral",
                "auteurs.nom",
                "auteurs.prenom",
                "mot_cles.text",
            ], fuzziness="auto")


class FilterArticles(PaginatedElasticSearchAPIView):
    serializer_class = ArticleSerializer
    document_class = ArticleDocument

    def generate_q_expression(self, query, filters):
        if 'authors' in filters:
            auteur_query = Q('terms', auteurs__nom=filters.get('authors', []))
        else:
            auteur_query = Q()    
        
        if 'keywords' in  filters:
            motCle_query = Q('terms', mot_cles__text=filters.get('keywords', []))
        else:
            motCle_query = Q()    

        if 'institutions' in filters:
            institution_query = Q('terms', auteurs__institutions__nom=filters.get('institutions', []))
        else:
            institution_query = Q()
        
        
        if 'start_date' in filters:
            start_date = filters['start_date']
            start_date_query = Q('range', date_de_publication={'gte': start_date})
        else:
            start_date_query = Q()
 
        if 'end_date' in filters:
            end_date = filters['end_date']
            end_date_query = Q('range', date_de_publication={'lte': end_date})
        else:
            end_date_query = Q()

        filter_query = auteur_query &  motCle_query &   institution_query &  start_date_query & end_date_query
        return filter_query

            
                
    

    
