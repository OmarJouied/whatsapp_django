from django.urls import path
from .views import index, user, messages

urlpatterns = [
    path('', index),
    path('user/', user),
    path('messages/', messages),
]