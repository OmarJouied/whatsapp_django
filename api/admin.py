from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Room)
admin.site.register(Group)
admin.site.register(View)
admin.site.register(Message)