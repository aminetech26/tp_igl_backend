from django.urls import path, include
from rest_framework import routers

from .views import ArticleFavorisViewSet

router = routers.DefaultRouter()
router.register(r"", ArticleFavorisViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
