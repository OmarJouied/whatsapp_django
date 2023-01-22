from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.conf import settings
import json

from .models import User, Room, Message, Group

import time

# Create your views here.
def index(request):
    if request.method == 'POST':
        username = json.loads(request.body).get("username")

        user_data = User.objects.get(username=username)
        
        rooms = user_data.room_set.all()

        connections = []

        for room in rooms:
            data = room.message_set.order_by('-id')[0] if room.message_set.exists() else room
            date = data.date

            if date.strftime("%D") == time.strftime("%D"):
                date = date.strftime('%H:%M')
            else:
                date = date.strftime('%m/%d/%y')

            connections.append({
                "id": room.pk,
                "shortcatMessage": data.content if room.message_set.exists() else "start new chat",
                "date": date,
                "unRead": 0
            })
            try:
                connections[-1]["name"] = room.group.label
                connections[-1]["avatar"] = room.group.avatar.url
            except:
                connection = room.connections.exclude(username=username)[0]
                connections[-1]["name"] = connection.username
                connections[-1]["avatar"] = connection.avatar.url

        return JsonResponse({
                "avatar": user_data.avatar.url,
                "connections": connections
            })

    return JsonResponse({
        "username": User(username="jouied") == None,#request.POST.get('username'),
        "connection": request.POST.get('connection'),
    })

def user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get('email'):
            password = data.get('password')
            confirm = data.get('confirm')
            if password != confirm:
                return JsonResponse({
                    "message": "password incorrect",
                    "error": 1
                })
            email = data.get('email')
            username = data.get('username')

            if Group.objects.filter(label=username):
                return JsonResponse({
                    "message": "change username",
                    "error": 1
                })

            try:
                user_instance = User.objects.create(email=email, username=username, password=make_password(password))
                isExist = True
            except:
                isExist = False

        else:
            try:
                user_instance = User.objects.get(username=data.get('username'))
                isExist = user_instance.check_password(data.get('password'))
            except:
                isExist = False
        return JsonResponse({
                "isExist": isExist
            })
    if request.method == 'PUT':
        if request.content_type.startswith('multipart'):
            put, files = request.parse_file_upload(request.META, request)

            avatar = files.getlist("avatar")
            body = put.dict()

            current_user = User.objects.get(username=body["username"])
            body.pop("username")

            if current_user.email == body["email"]:
                body.pop("email")
            
            if current_user.check_password(body.get("password")):
                body.pop("password")

            if avatar:
                # implement the logic of deleting old image before saving the new
                # end login
                current_user.avatar = avatar[0]
            else:
                body.pop("avatar")

            keys = list(filter(lambda item: body[item], body.keys()))

            for key in keys:
                if key == "password":
                    body[key] = make_password(body[key])
                setattr(current_user, key, body[key])

            current_user.save()

            return JsonResponse({
                "error": 0
            })
    
    current_user = User.objects.get(username=request.GET["username"])
    
    return JsonResponse({
        "avatar": current_user.avatar.url,
        "email": current_user.email,
    })

def messages(request):
    req = json.loads(request.body)

    name = req["name"]
    
    group = Group.objects.filter(label=name)
    if group:
        room = group[0].room
        target = group[0]
    elif not User.objects.filter(username=name):
        return JsonResponse({
            "message": "no user like this!",
            "error": 1
        })
    else:
        username = req["username"]
        room = Room.objects.filter(connections__username=username).filter(connections__username=name)
        target = User.objects.get(username=name)
    
    messages_room = [{"id": message_room.pk, "content": message_room.content, "username": message_room.owner.username, "date": message_room.date.strftime('%m/%d/%y-%H:%M')} for message_room in ((room if group else room[0]).message_set.all() if room else [])]

    return JsonResponse({
        "avatar": target.avatar.url,
        "messages": messages_room,
        "is_opened": (room if group else room[0]).is_opened if room else True,
    }, safe=False)
