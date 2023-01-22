from django.urls import re_path
from .consumers import *

ws_urlpatterns = [
    re_path('ws/profile/(?P<username>\w+)/$', AdminInteract.as_asgi()),
    re_path('ws/(?P<username>\w+)/$', WSConsumer.as_asgi()),
    re_path('ws/$', OnLine.as_asgi()),
]