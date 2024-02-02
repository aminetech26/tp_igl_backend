from django.urls import path, include
from rest_framework import routers

from .views import ModerationView

router = routers.DefaultRouter()
router.register(r"", ModerationView, basename='moderation')

urlpatterns = [
    path("", include(router.urls)),
]
