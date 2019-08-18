from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import generics

from .models import *
from .serializers import *

from django.http import Http404, HttpResponseRedirect, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
import random, requests, time, string
from django.conf import settings
from string import ascii_uppercase
from django.urls import reverse
from rest_framework.viewsets import ModelViewSet

from rest_framework_extensions.mixins import NestedViewSetMixin

from django.contrib.auth.models import User

import sys, os
sys.path.append(os.path.abspath("../player_example/"))
import smartmonkey
import randomstone

from .forms import *

import pytz
utc = pytz.UTC
from datetime import datetime
import threading


def home(request):
        return render(request, 'home.html')


def makeRandomString():
    randomStream=""
    for i in range(0,8):
        randomStream += str(random.choice(string.ascii_letters+string.digits))
    return randomStream


def single(request):
    if request.method == 'POST':
        form = single_form(request.POST)

        if form.is_valid():
            player = form.cleaned_data['player_name']
            if not Session.objects.filter(session_name=player).exists():
                colorNum = random.randrange(1,3)
                if colorNum == 1:
                    wid = makeRandomString()
                    s = whiteSession(colorid=wid, session_name=player, status=0, name=player)
                    s.save()
                    bid = makeRandomString()
                    s = blackSession(colorid=bid, session_name=player, status=0, name="Monkey")
                    s.save()
                    s = Session(session_name=player, blackid=bid, whiteid=wid, status=False, mode="S")
                    s.save()
                else :
                    wid = makeRandomString()
                    s = whiteSession(colorid=wid, session_name=player, status=0, name="Monkey")
                    s.save()
                    bid = makeRandomString()
                    s = blackSession(colorid=bid, session_name=player, status=0, name=player)
                    s.save()
                    s = Session(session_name=player, blackid=bid, whiteid=wid, status=False, mode="S")
                    s.save()
                randomstone.random_stone(request,player)   
            return HttpResponseRedirect(reverse(guide, kwargs={'room':player})) 
    else:
        form = single_form()
    return render(request, 'single_form.html', {'form': form})


def double(request):
    if request.method == 'POST':
        form = double_form(request.POST)

        if form.is_valid():
            room = form.cleaned_data['room_name']
            player1 = form.cleaned_data['player1_name']
            player2 = form.cleaned_data['player2_name']

            if not Session.objects.filter(session_name=room).exists():

                colorNum = random.randrange(1,3)
                if colorNum == 1:
                    wid = makeRandomString()
                    s = whiteSession(colorid=wid, session_name=room, status=0, name=player1)                                          
                    s.save()                                                                                               
                    bid = makeRandomString()                                                                               
                    s = blackSession(colorid=bid, session_name=room, status=0, name=player2)
                    s.save()                                                                                               
                    s = Session(session_name = room, blackid=bid, whiteid=wid, status=False, mode="D")                      
                    s.save()
  
                else :
                    wid = makeRandomString()
                    s = whiteSession(colorid=wid, session_name=room, status=0, name=player2)
                    s.save()
                    bid = makeRandomString()
                    s = blackSession(colorid=bid, session_name=room, status=0, name=player1)
                    s.save()
                    s = Session(session_name = room, blackid=bid, whiteid=wid, status=False, mode="D")
                    s.save()

                randomstone.random_stone(request,room)   
      
            return HttpResponseRedirect(reverse(guide, kwargs={'room':room}))
    else:
        form = double_form()
    return render(request, 'double_form.html', {'form': form})


def guide(request,room):
    if Session.objects.filter(session_name=room).exists():
        s = Session.objects.get(session_name=room)
        ws = whiteSession.objects.get(session_name=room)
        bs = blackSession.objects.get(session_name=room)
    else:
        return redirect('home')

    if request.method == 'POST':
        return HttpResponseRedirect(reverse(double_game, kwargs={'session_key':room}))
    else:
        return render(request, 'guide.html', {'room_name':room, 'P1_key': bs.colorid, 'P2_key': ws.colorid, 'P1': bs.name, 'P2': ws.name, 'P1_color': "black", 'P2_color': "white"})

def double_game(request, session_key):
    if Session.objects.filter(session_name=session_key).exists():
        s = Session.objects.get(session_name=session_key)
        bs = blackSession.objects.get(session_name=session_key)
        ws = whiteSession.objects.get(session_name=session_key)
        url = request.build_absolute_uri('/')[:-1]
        if bs.name == "Monkey":
            requests.get(url+"/api/sessions/"+bs.session_name+"/stones/?colorid="+bs.colorid)
        elif ws.name=="Monkey":
            requests.get(url+"/api/sessions/"+ws.session_name+"/stones/?colorid="+ws.colorid)
        return render(request, 'double_room.html', {'room_name': session_key, 'P1': bs.name, 'P2': ws.name, 'P1_color': "black", 'P2_color': "white"})
    else:
        return redirect('home')

def enter(self, player):
    if player.status == 0:
        player.status = 1
        player.save()

        s = Session.objects.get(session_name=player.session_name)
        bs = blackSession.objects.get(colorid=s.blackid)
        ws = whiteSession.objects.get(colorid=s.whiteid)

        if player.colorid == s.whiteid:
            if bs.status == 1:
                s.status = True
                s.save()
                bs.status = 2
                bs.save()
            if bs.name == "Monkey":
                x = threading.Thread(target=callmonkeytwo, args=(self.request, s.session_name, bs.colorid, "black"))
                x.start()

        elif player.colorid == s.blackid:
            if ws.status == 1:
                s.status = True
                s.save()
                bs.status = 2
                bs.save()
            if ws.name == "Monkey":
                x = threading.Thread(target=callmonkeytwo, args=(self.request, s.session_name, ws.colorid, "white"))
                x.start()



def callmonkey(request, session_name, colorid):
    time.sleep(3)
    smartmonkey.first_stone(request, session_name, colorid)


def double_status(request, session_key):
    if Session.objects.filter(session_name=session_key).exists():
        bs = blackSession.objects.get(session_name=session_key)
        ws = whiteSession.objects.get(session_name=session_key)
        s = Session.objects.get(session_name=session_key)
        if s.status is True:
            player1_status = "entering"
            player2_status = "entering"
        else:
            player1_status = "waiting..."
            player2_status = "waiting..."
            if bs.status >= 1:
                player1_status = "entering"
            if ws.status >= 1:
                player2_status = "entering"
        status = {'player1_status' : player1_status , 'player2_status' : player2_status}
        return JsonResponse(status, safe=False)
    return HttpResponse()          

def double_timer(request, session_key):
    if Session.objects.filter(session_name=session_key).exists():
        bs = blackSession.objects.get(session_name=session_key)
        ws = whiteSession.objects.get(session_name=session_key)
        s = Session.objects.get(session_name=session_key)
        
        timer = {'black_timer' : bs.timer , 'white_timer' : ws.timer}
        return JsonResponse(timer, safe=False)
    return HttpResponse()

def watch(request):
    return render(request, 'list.html')


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def timer(count, gettime, key, colorid):
    if Session.objects.get(session_name=key).blackid == colorid:
        ts = blackSession.objects.get(session_name=key)
    elif Session.objects.get(session_name=key).whiteid == colorid:
        ts = whiteSession.objects.get(session_name=key)
    count-=1
    ts.timer = count
    ts.save()
    posttime = ts.post_time
    
    t = threading.Timer(1, timer, args=[count, gettime, key, colorid])
    t.start()

    if posttime is not None:
        if gettime < posttime:
            t.cancel()

    if count == 1:
        ts.status = False
        ts.save()
        t.cancel()



class SessionViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()

class BlackSessionViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = BlackSessionSerializer
    queryset = blackSession.objects.all()

class WhiteSessionViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = WhiteSessionSerializer
    queryset = whiteSession.objects.all()
 
class StoneViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = StoneSerializer
    queryset = ResultOmok.objects.all()

    def get_queryset(self):
        gettime = utc.localize(datetime.now())
        room = self.kwargs['parent_lookup_room']
        s = Session.objects.get(session_name=room)
        bs = blackSession.objects.get(session_name=room)
        ws = whiteSession.objects.get(session_name=room)
        colorid = self.request.GET.get('colorid', None)

        results = ResultOmok.objects.filter(room=room)
        laststone = results.last()

        if colorid == "admin":
            return results
        elif colorid == s.blackid: #Black이 Get 했을 때
            if bs.status == 2:
            #elif laststone.color=="white":
                bs.status = 3
                bs.save()
                if results.last().color=="white":
                    timer(8, gettime, room, colorid)
            elif bs.status == 0:
                enter(self, bs)
            return results
        elif colorid == s.whiteid: #White가 Get 했을 때
            if ws.status == 2:
            #elif laststone.color=="black":
                ws.status = 3
                ws.save()
                timer(8, gettime, room, colorid)
            elif ws.status == 0:
                enter(self, ws)
            return results
        else:
            print("Cannot Access")

class BlackViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = BlackSerializer
    queryset = Black.objects.all()

    def create(self, request, *args, **kwargs):
        s = blackSession.objects.get(colorid=self.kwargs['parent_lookup_room'])
        s.post_time = utc.localize(datetime.now())
        s.timer = 7
        ss = Session.objects.get(session_name = s.session_name)
        ws = whiteSession.objects.get(session_name=s.session_name)
        if ss.status is False:
            raise Exception('Status False')
        elif s.status < 3:
            raise Exception('Status False')
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)

            blacks = Black.objects.filter(room=s.colorid)
            tmp = blacks.last()

            resultRoom = s.session_name
            resultColor = "black"
            resultS1 = tmp.s1
            resultS2 = tmp.s2
            resultX1 = resultS1[0]
            resultY1 = resultS1[1:]
            turn = 0
            if resultColor != 'red':
                turn = ResultOmok.objects.filter(room=resultRoom).count() - 6
            resultOmok = ResultOmok(room=resultRoom, color = resultColor, x = resultX1 , y = resultY1, turn=turn)
            resultOmok.save()


            if len(resultS2) == 0:
                resultX2 = ""
                resultY2 = 0 
            else:
                resultX2 = resultS2[0]
                resultY2 = resultS2[1:]
            
                if resultColor != 'red':
                    turn = ResultOmok.objects.filter(room=resultRoom).count() - 6
                resultOmok = ResultOmok(room=resultRoom, color = resultColor, x = resultX2 , y = resultY2, turn=turn)
                resultOmok.save()

            s.status = 1
            ws.status = 2
            s.save()
            ws.save()
#            if ws.name == "Monkey":
#                x = threading.Thread(target=callmonkeytwo, args=(request, resultRoom, ws.colorid, "white"))
#                x.start()

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def callmonkeytwo(request, room, colorid, color):
    time.sleep(3)
    smartmonkey.second_stone(request, room, colorid, color)


class WhiteViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = WhiteSerializer
    queryset = White.objects.all()
    
    def create(self, request, *args, **kwargs):
        s = whiteSession.objects.get(colorid=self.kwargs['parent_lookup_room'])
        s.post_time = utc.localize(datetime.now())
        s.timer = 7
        ss = Session.objects.get(session_name = s.session_name)
        if ss.status is False:
            raise Exception('Status False')
        elif s.status < 3:
            raise Exception('Status False')
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)

            whites = White.objects.filter(room=s.colorid)
            tmp = whites.last()

            resultRoom = s.session_name
            resultColor = "white"
            resultS1 = tmp.s1
            resultS2 = tmp.s2
            resultX1 = resultS1[0]
            resultY1 = resultS1[1:]
            resultX2 = resultS2[0]
            resultY2 = resultS2[1:]
            turn = 0 
 
            if resultColor != 'red':
                turn = ResultOmok.objects.filter(room=resultRoom).count() - 6    
            resultOmok = ResultOmok(room=resultRoom, color = resultColor, x = resultX1 , y = resultY1, turn=turn)

            resultOmok.save()

            if resultColor != 'red':
                turn = ResultOmok.objects.filter(room=resultRoom).count() - 6    
            resultOmok = ResultOmok(room=resultRoom, color = resultColor, x = resultX2 , y = resultY2, turn=turn)
          
            resultOmok.save()

            bs = blackSession.objects.get(session_name=s.session_name)
            s.status = 1
            bs.status = 2
            s.save()
            bs.save()
#            if bs.name == "Monkey":
#                x = threading.Thread(target=callmonkeytwo, args=(request,resultRoom, bs.colorid, "black"))
#                x.start()

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def ResultData(request, sessionid):
    tmp = ResultOmok.objects.filter(room=sessionid)
    black = tmp.filter(color="black")
    white = tmp.filter(color="white")

    bCount = black.count()
    wCount = white.count()

    s=None

    if Session.objects.filter(session_name=sessionid).exists():
        s = Session.objects.get(session_name=sessionid)

    if bCount <= 6 or wCount <= 6 :
        return HttpResponse()

    row = list(ascii_uppercase)[:-7]
    
    for i in row:
        if black.filter(x=i).exists():
            black_x = black.filter(x=i)    
            for j in black_x:
                if black_x.count() >= 6:
                    cnt = 1
                    for jj in range(1,6):
                        if black.filter(x=i, y=j.y+jj).exists() == False:
                            break
                        cnt += 1
                    if cnt == 6:
                        result = str("Black WIN !!!")
                        if s is not None:
                            s.status = False
                            s.save()
                        return JsonResponse(result, safe=False)
                    else:
                        cnt = 1
                if black.filter(x=chr(ord(i)+1), y=j.y).exists():
                    cnt = 2
                    for jj in range(2,6):
                        if black.filter(x=chr(ord(i)+jj), y=j.y).exists() == False:
                            break
                        cnt += 1
                    if cnt == 6:
                        result = str("Black WIN !!!")
                        if s is not None:
                            s.status = False
                            s.save()
                        return JsonResponse(result, safe=False)
                if black.filter(x=chr(ord(i)+1), y=j.y+1).exists():
                    cnt = 2
                    for jj in range(2,6):
                        if black.filter(x=chr(ord(i)+jj), y=j.y+jj).exists() == False:
                            break
                        cnt += 1
                    if cnt == 6:
                        result = str("Black WIN !!!")
                        if s is not None:
                            s.status = False
                            s.save()
                        return JsonResponse(result, safe=False)
                if black.filter(x=chr(ord(i)+1), y=j.y-1).exists():
                    cnt = 2
                    for jj in range(2,6):
                        if black.filter(x=chr(ord(i)+jj), y=j.y-jj).exists() == False:
                            break
                        cnt += 1
                    if cnt == 6:
                        result = str("Black WIN !!!")
                        if s is not None:
                            s.status = False
                            s.save()
                        return JsonResponse(result, safe=False)              

        if white.filter(x=i).exists():
            white_x = white.filter(x=i)   
            for j in white_x: 
                if white_x.count() >= 6:
                    cnt = 1
                    for jj in range(1,6):
                        if white.filter(x=i, y=j.y+jj).exists() == False:
                            break
                        cnt += 1
                    if cnt == 6:
                        result = str("White WIN !!!")
                        if s is not None:
                            s.status = False
                            s.save()
                        return JsonResponse(result, safe=False)
                    else:
                        cnt = 1
                if white.filter(x=chr(ord(i)+1), y=j.y).exists():
                    cnt = 2
                    for jj in range(2,6):
                        if white.filter(x=chr(ord(i)+jj), y=j.y).exists() == False:
                            break
                        cnt += 1
                    if cnt == 6:
                        result = str("White WIN !!!")
                        if s is not None:
                            s.status = False
                            s.save()
                        return JsonResponse(result, safe=False)
                                   
                if white.filter(x=chr(ord(i)+1), y=j.y+1).exists():
                    cnt = 2
                    for jj in range(2,6):
                        if white.filter(x=chr(ord(i)+jj), y=j.y+jj).exists() == False:
                            break
                        cnt += 1
                    if cnt == 6:
                        result = str("White WIN !!!")
                        if s is not None:
                            s.status = False
                            s.save()
                        return JsonResponse(result, safe=False)
                 
                if white.filter(x=chr(ord(i)+1), y=j.y-1).exists():
                    cnt = 2
                    for jj in range(2,6):
                        if white.filter(x=chr(ord(i)+jj), y=j.y-jj).exists() == False:
                            break
                        cnt += 1
                    if cnt == 6:
                        result = str("White WIN !!!")
                        if s is not None:
                            s.status = False
                            s.save()
                        return JsonResponse(result, safe=False)              
            
    return HttpResponse()
