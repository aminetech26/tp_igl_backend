from django.contrib import admin
from django.urls import path
from .views import RegisterView , LoginView , LogoutView , UserView , RefreshView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('refresh', RefreshView.as_view()),
#for testing
    path('userView', UserView.as_view()),

]