from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils import dateparse
from drawSomething.forms import *
from django.core.exceptions import ObjectDoesNotExist
from drawSomething.models import *
from django.http import HttpResponse, Http404
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail
from dwebsocket import require_websocket, accept_websocket
import json
import random;
import re

# Create your views here.
def welcome(request):
    context = {}
    return render(request, 'welcome.html', context)

@login_required
def globalpage(request):
    if request.method == 'GET':
        currentuser = Users.objects.get(Userobj = request.user)
        allusers = Users.objects.exclude(id = currentuser.id)
        allrooms = Rooms.objects.all()
        context={'notfound':False, 'notgoundroom':False, 'allusers':allusers, 'roomlist':allrooms, 'currentusername':request.user.username}
        return render(request,'globalpage.html',context)
    
    currentuser = Users.objects.get(Userobj = request.user)
    allusers = Users.objects.exclude(id = currentuser.id)
    allrooms = Rooms.objects.all()
    if 'searchusersbar' in request.POST:
        username = request.POST['searchusersbar']
        try:
            searchuser = Users.objects.get(Username = username)
            if currentuser == searchuser:
                context = {'notfound':True, 'notgoundroom':False, 'allusers':allusers, 'roomlist':allrooms,'currentusername':request.user.username}
                return render(request,'globalpage.html',context)
            else:
                allusers = Users.objects.exclude(Username = username)
                context = {'searchuser':searchuser, 'notfound':False, 'notgoundroom':False, 'allusers':allusers, 'roomlist':allrooms,'currentusername':request.user.username}
                return render(request,'globalpage.html',context)
        except ObjectDoesNotExist:
            context = {'notfound':True, 'notgoundroom':False, 'allusers':allusers, 'roomlist':allrooms,'currentusername':request.user.username}
            return render(request,'globalpage.html',context)
   

    if 'searchroombar' in request.POST:
        roomname = request.POST['searchroombar']
        try:
            searchroom = Rooms.objects.get(Roomname = roomname)
            allrooms = Rooms.objects.exclude(Roomname = roomname)
            context = {'searchroom':searchroom, 'notfound':False, 'notgoundroom':False,'allusers':allusers, 'roomlist':allrooms, 'currentusername':request.user.username}
            return render(request,'globalpage.html',context)
        except ObjectDoesNotExist:
            context = {'notfound':False, 'notgoundroom':True, 'allusers':allusers, 'roomlist':allrooms, 'currentusername':request.user.username}
            return render(request,'globalpage.html',context)
    
    if 'add_friend' in request.POST:
        friendid = request.POST['add_friend']
        frienduser = User.objects.get(id = friendid)
        currentuser = Users.objects.get(Userobj = request.user)
        currentuser.Friendlist.add(frienduser)
        context={'notfound':False, 'notgoundroom':False, 'allusers':allusers, 'roomlist':allrooms, 'currentusername':request.user.username}
        return render(request,'globalpage.html',context)
    if 'enter_room' in request.POST:
        roomid  = request.POST['enter_room']
        url_room = 'room/' + roomid
        room_to_enter = get_object_or_404(Rooms, id=roomid)
        print(room_to_enter.Roomname)
        # judge if the room is full
        # changeable room size
        room_size = 3
        if (room_to_enter.players.count() < room_size):
            room_to_enter.players.add(request.user)
            print(room_to_enter.players.all())
            if (room_to_enter.players.count() == room_size):
                room_to_enter.Gamestate = True
                room_to_enter.word = pickGuessWord()
                room_to_enter.painterName = pickPainter(roomid, room_to_enter.players.all())
                room_to_enter.save()

            return redirect(url_room)
        elif (room_to_enter.players.filter(id=request.user.id)):
            return redirect(url_room)
            # if the user is already in the room
        else:
            context={'notfound':False, 'notgoundroom':False, 'allusers':allusers, 'roomlist':allrooms, 'currentusername':request.user.username, 'errormessage':'The room is full!Try another one.'}
            return render(request,'globalpage.html',context)
    

    context={'notfound':False, 'notgoundroom':False, 'allusers':allusers, 'roomlist':allrooms, 'currentusername':request.user.username}
    return render(request,'globalpage.html',context)

def pickGuessWord():
    #wait for new word
    words =['cat', 'pig', 'dog','rabbit', 'mouse', 'elephant', 'panda', 'tiger', 'duck', 'fish', 'bird', 'monkey', 'baby',
    'chicken', 'lion', 'sheep', 'horse', 'wolf', 'snake', 'bear', 'cow', 'hair', 'eye', 'ear', 'nose', 'face', 'neck',
    'foot', 'mouth', 'hand', 'finger', 'sunny', 'cloudy', 'windy', 'bike', 'plane', 'train', 'ship', 'subway', 'taxi',
    'jeep', 'motor', 'boat', 'rice', 'noodles', 'egg', 'cake', 'bread', 'hot dog', 'hamburger', 'soup', 'chicken', 'meat',
    'pork', 'eggplant', 'tomato', 'potato', 'coffee', 'juice', 'ice-cream', 'milk', 'orange', 'apple', 'pear', 'strawberry',
    'banana', 'grapes', 'lemon', 'peach', 'watermelon', 'doctor', 'driver', 'singer', 'nurse', 'teacher', 'writer', 'engineer',
    'artist', 'policeman', 'salesperson',  'T-shirt', 'skirt', 'dress', 'jacket', 'coat', 'coat', 'boots', 'jeans', 'slippers',
    'bathroom', 'classroom', 'gym', 'library', 'cinema', 'zoo', 'star', 'moon', 'rainbow', 'forest', 'hurt', 'angry', 'sleep',
    'skiing', 'ping-pong', 'football', 'piano', 'chess', 'violin', 'light', 'sofa', 'window', 'blackboard', 'computer', 'newspaper'
    ]
    word = random.sample(words, 1)
    print("word to guess:", word[0])
    return word[0]

def pickPainter(roomid, players):
    player_name = []
    for p in players:
        player_name.append(p.username)

    painter = random.sample(player_name, 1)
    print("painter", painter[0])
    return painter[0]

@login_required
def room(request,room_id):
    context = {}
    room = get_object_or_404(Rooms, id=room_id)
    if request.method == 'GET':         
        context['room'] = room
        context['currentusername']=request.user.username
        context['players'] = room.players.all()

        return render(request,'room.html',context)

    if 'quit_room' in request.POST:
        currentuser = request.user
        room.players.remove(currentuser.id)
        return redirect('globalpage')
    context['room'] = room
    context['currentusername']=request.user.username
    context['players'] = room.players.all()

    return render(request,'room.html',context)

@login_required
def refreshDrawStat(request):
    room_id = request.GET['roomid']
    room = Rooms.objects.get(id=room_id)
    room_size = 3
    if (room.players.count() != room_size):
        room.Gamestate = False
        room.save()
    else: 
        if not room.Gamestate:
            room.Gamestate = True
            room.word = pickGuessWord()
            room.painterName = pickPainter(room_id, room.players.all())
            room.save()        

    flag = room.Gamestate
    word = room.word
    painter = room.painterName
    response_text = json.dumps({'flag': flag, 'word': word, 'painter': painter})
    
    return HttpResponse(response_text, content_type='application/json')

@login_required
def refresh_room(request):
    room_id = request.GET['roomid']
    room = Rooms.objects.get(id=room_id)
    players = []
    for p in room.players.all():
        players.append({
            'id': p.id,
            'username': p.username,

        })
    response_text = json.dumps({'players': players})
    return HttpResponse(response_text, content_type='application/json')

clients=[]
for i in range(10):
    clients.append([])

@login_required
@accept_websocket
def socket(request):
    if request.is_websocket():
        win_status = False   
        while True:
            message=request.websocket.wait()
            if not message:
                break
            else:
                msg=str(message)
                print('message is')
                print(msg)
                data = msg.split('&')
                data[-1] = re.sub("\D", "", data[-1])
                room_id = int(data[-1])
                print(room_id)
                if request.websocket not in clients[room_id]:
                    clients[room_id].append(request.websocket)
                print(clients)
                if data[0].find('post') != -1:
                    print('post')
                    data[4] = re.sub("\D", "", data[4])
                    print(data[4])
                    curr_room = get_object_or_404(Rooms, id=data[4])
                    if data[1] == curr_room.word:
                        if curr_room.Gamestate:
                            win_status = True
                            currentuser = Users.objects.get(Userobj = request.user)
                            curr_room.winner = currentuser.Username
                            curr_room.save()
                #print('loop start')
                if msg.find('handshake') == -1:
                    for client in clients[room_id]:
                        if client != request.websocket:
                            # print('others')
                            client.send(message)
                        else:
                            if msg.find('post') != -1:
                                # print('me for posting')
                                client.send(message)
                        if win_status:
                            # print('any cats?')
                            client.send('win')
                        #print(client)
                #print('loop end')
    # if userid in clients:
        # del clients[userid]
        # print(str(userid) + "out")

@login_required
def win(request, room_id):
    room_size = 3
    room = get_object_or_404(Rooms, id=room_id)
    currentuser = request.user
    winner = room.winner
    word = room.word
    if request.method == 'GET' :
        for p in room.players.all():
            room.players.remove(p.id) 
        room.Gamestate = False   
        if (room.painterName):
             room.painterName = ""
        if (room.word):
             room.word= ""
        if (room.winner):
             room.winner= ""
        room.save()
        context = {'winner':winner, 'word':word}
    if 'end_game' in request.POST:        
        return redirect(reverse('globalpage'))
    if 'restart_game' in request.POST:
        # print('restart')
        url_room = '../room/' + str(room_id)
        if (room.players.count() < room_size):
            room.players.add(currentuser.id)
            if (room.players.count() == room_size):
                room.Gamestate = True
                room.word = pickGuessWord()
                room.painterName = pickPainter(room_id, room.players.all())
                room.save()

            return redirect(url_room)
        else:
            # need to add error message
            return redirect(globalpage)
    return render(request, "win.html",context)
    
def register(request):
    context = {}
    if request.method == 'GET':
        context['form'] =register_form()
        return render(request,"register.html",context)

    form = register_form(request.POST,request.FILES)
    context['form'] = form

    if not form.is_valid():
        return render(request,'register.html',context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email']
                                        )
    new_user.save()
    new_user = authenticate(username = form.cleaned_data['username'],password = form.cleaned_data['password'])
    login(request,new_user)

    NewUser = Users(Userobj = new_user,
                    Username=form.cleaned_data['username'],
                    Password=form.cleaned_data['password'],
                    Email=form.cleaned_data['email'],
                    Description = form.cleaned_data['description'],
                    Picture = form.cleaned_data['picture'],
                    )
    NewUser.save()
    return redirect(reverse('globalpage'))

def log(request):
    context = {}
    if request.method == 'GET':
        context['form'] = login_form()
        return render(request,"login.html",context)
    
    form = login_form(request.POST)
    context['form'] = form

    if not form.is_valid():
        context["errormessage"] = "Wrong username/password"
        return render(request,'login.html',context)

    new_user = authenticate(username = form.cleaned_data['username'],password = form.cleaned_data['password'])
    login(request,new_user)
    return redirect(reverse('globalpage'))

@login_required
def sendemail(request):
    context = {}
    currentuser = Users.objects.get(Userobj = request.user)
    friendlist = currentuser.Friendlist.all()
    if request.method == 'POST':
        if 'invite_button' in request.POST:
            friendid = request.POST['invite_button']
            friend = User.objects.get(id = friendid)
            email = friend.email
            sender = 'doriswm@163.com'
            send_mail('Invitation from Drawsomwthing', 'You are invited by '+ request.user.username , sender,
                [email, sender], fail_silently=False)
    context = {'friendlist':friendlist, 'currentusername':request.user.username}    
    return render(request, 'roomcreationpage.html', context)

@login_required
def roomcreationpage(request):
    context={}
    if request.method == 'GET':
        currentuser = Users.objects.get(Userobj = request.user)
        friendlist = currentuser.Friendlist.all()
        context = {'friendlist':friendlist, 'currentusername':request.user.username}
        return render(request, 'roomcreationpage.html', context)
    
    currentuser = Users.objects.get(Userobj = request.user)
    friendlist = currentuser.Friendlist.all()

    if 'roomname' in request.POST:
        try:
            roomname = request.POST['roomname']
            searchroom = Rooms.objects.get(Roomname = roomname)
            context = {'friendlist':friendlist, 'currentusername':request.user.username, 'error':'The room name is already taken, please try another'}
            return render(request, 'roomcreationpage.html', context)
        except ObjectDoesNotExist:
            new_room = Rooms()
            new_room.Roomname = request.POST['roomname']
            if request.POST['roomPrivacy'] == 'private':
                new_room.Roomstate = False
            new_room.Roomdescription = request.POST['description']
            new_room.Roomcreator = request.user
            number = random.randint(1,6)
            new_room.backgroundphoto = 'img/bg'+str(number)+'.jpg'
            
            new_room.save()
            new_room.players.add(request.user)

            new_room.save()
            print(new_room.players.all()) 
            url_room = 'room/'+str(new_room.id)
            return redirect(url_room)

    context = {'friendlist':friendlist, 'currentusername':request.user.username}
    return render(request, 'roomcreationpage.html', context)

@login_required
def get_photo(request,id):
    cuser = get_object_or_404(Users, id = id)
    if not cuser.Picture:
        raise Http404
    return HttpResponse(cuser.Picture)


@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


