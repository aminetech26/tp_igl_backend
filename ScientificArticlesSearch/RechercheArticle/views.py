import abc

from django.http import HttpResponse
from elasticsearch_dsl import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from Articles.documents import ArticleDocument
from .serializers import ArticleSearchResultSerializer


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
    serializer_class = ArticleSearchResultSerializer
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
