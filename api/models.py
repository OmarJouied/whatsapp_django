from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

import random
import string

def generate_room_name():
    return "".join(random.choices(string.ascii_letters+"0123456789_", k=3)) + '-' +\
            "".join(random.choices(string.ascii_letters+"0123456789_", k=3)) + '-' +\
            "".join(random.choices(string.ascii_letters+"0123456789_", k=3))

# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(upload_to='%y/%m/%d', default="userLogo.svg")

    def __str__(self):
        return self.username

class Room(models.Model):
    name = models.CharField(max_length=11, blank=True, default=generate_room_name)
    connections = models.ManyToManyField(User)
    is_opened = models.BooleanField(blank=True, default=True)
    date = models.DateTimeField(blank=True, default=timezone.now)

    def __str__(self):

        return f"{self.name} room contains {self.connections.count()} users!"

class Group(models.Model):
    label = models.CharField(max_length=50)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='%y/%m/%d', default="groupLogo.svg")
    room = models.OneToOneField(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.admin.username} admin of {self.label} group!"

class View(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_view_it = models.BooleanField(blank=True, default=False)
    is_deleted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.user.username

class Message(models.Model):
    content = models.CharField(max_length=2000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    related_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(blank=True, default=timezone.now)
    views = models.ManyToManyField(View, blank=True)
    room = models.ManyToManyField(Room)

    def __str__(self):

        return f"{self.owner.username} say {self.content} in {self.room.all()[0].name} room!"
