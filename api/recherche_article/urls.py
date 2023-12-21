from django.urls import path

from .views import SearchArticles , FilterArticles

urlpatterns = [
    path("<str:query>/", SearchArticles.as_view()),
    # we need to make an url for filtering article as I also use the queries sent in the url
    # path("<str:query>/", SearchArticles.as_view())
]
