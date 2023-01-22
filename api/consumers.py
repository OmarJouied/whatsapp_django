from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.conf import settings

import json
import time
from urllib.parse import unquote

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import User, Message, Room, Group

class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.room_name = False
        async_to_sync(self.channel_layer.group_add)(self.username, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.username, self.channel_name)

    def receive(self, text_data):
        data_from_user = json.loads(text_data)

        if data_from_user.get("target"):
            if self.room_name:
                async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)
            self.room_name = data_from_user.get("target")
            async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
            if data_from_user.get("clear"):
                room = Room.objects.filter(connections__username=self.username).filter(connections__username=self.room_name)
                if room:
                    # room[0].connections.clear(User.objects.get(username=self.username))
                    print(1)
                pass
        else:
            group = Group.objects.filter(label=self.room_name)
            if group:
                pass
            elif not User.objects.filter(username=self.room_name):
                pass
            else:
                room = Room.objects.filter(connections__username=self.username).filter(connections__username=self.room_name)
                if room:
                    room = room[0]
                else:
                    room = Room()
                    room.save()
                    room.connections.add(User.objects.get(username=self.username))
                    room.connections.add(User.objects.get(username=self.room_name))
                
                if data_from_user.get("message"):
                    message = Message(content=data_from_user.get("message"), owner=User.objects.get(username=self.username))
                    message.save()
                    message.room.add(room)

                    async_to_sync(self.channel_layer.group_send)(self.room_name, {"type": "chat_message", "data": {
                        "message": {
                            "id": message.pk,
                            "room": self.room_name,
                            "username": self.username,
                            "content": message.content,
                            "date": message.date.strftime("%m/%d/%y-%H:%M"),
                        }
                    }})
    
    def chat_message(self, event):
        self.send(text_data=json.dumps({"data": event["data"]}))

class OnLine(WebsocketConsumer):
    def connect(self):
        self.accept()

class AdminInteract(WebsocketConsumer):
    def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.accept()
    
    def receive(self, text_data):
        self.user = User.objects.get(username=self.username)
        self.rooms = [room.connections.exclude(username=self.username)[0].username for room in Room.objects.filter(connections__username=self.username)]
        self.rooms = [self.username, *self.rooms]

        if json.loads(text_data):
            pass
        else:
            for room in self.rooms:
                # if not hasattr(room, 'group'):
                    async_to_sync(self.channel_layer.group_send)(room, {"type": "chat_message", "data": {
                        "message": {
                            "username": self.username,
                            "avatar": self.user.avatar.url
                        }
                    }})
