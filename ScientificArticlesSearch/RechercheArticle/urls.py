from django.urls import path

from .views import SearchArticles , FilterArticles

urlpatterns = [
    path("<str:query>/", SearchArticles.as_view()),
]