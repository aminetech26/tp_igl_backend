import abc

from django.http import HttpResponse
from elasticsearch_dsl import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from articles.documents import ArticleDocument
from articles.serializers import ArticleSerializer


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
        base_query = Q(
            "multi_match",
            query=query,
            type="most_fields",
            fields=[
                "titre",
                "textIntegral",
                "auteurs.nom",
                "auteurs.prenom",
                "auteurs.institutions.nom",
                "auteurs.institutions.ville",
                "mot_cles.text",
                "references_bibliographique.nom",
            ], fuzziness="auto")
        if filters:
            filter_queries = [Q("term", **{field: value}) for field, value in filters.items()]
            filters_query = Q("bool", must=filter_queries)
            final_query = base_query & filters_query
        else:
            final_query = base_query
        return final_query
