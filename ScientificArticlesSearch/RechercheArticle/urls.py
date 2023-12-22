from django.urls import path

from .views import SearchArticles

urlpatterns = [
    path("<str:query>/", SearchArticles.as_view()),
]