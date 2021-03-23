# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
async_mode = None

import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from uuid import uuid4
from urllib.parse import urlencode
from rapidjson import dumps, UM_HEX

import socketio

basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.Server(async_mode=async_mode, logger=True, engineio_logger=True)
thread = None

numClients = {}

#Remove this
def call_test(request):
    return render(request,'call_test.html')
#

def index(request):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return HttpResponse(open(os.path.join(basedir, 'templates/index.html')))

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(10)
        count += 1
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')

def user_preferences(request):
    roomId = request.GET.get('roomId')
	
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return render(request, "user_preferences.html", {"roomId":roomId})

def call(request):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return render(request, "call.html", {})

def left(request):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    
    return render(request, 'left.html')

@sio.event
def generate(sid,message):
    roomId = message['roomId']

    if (roomId == "None"):
        val = uuid4()
        val = dumps(val, uuid_mode=UM_HEX)
        val = val.replace('"', '')
    else:
        val = roomId

    base_url = '/join/call'
    query_string =  urlencode({'roomId': val})
    url = '{}?{}'.format(base_url,query_string)
                
    sio.emit('redirect',{'url':url}, to=sid)

@sio.event
def get_clients(sid, data):
    roomId = data['roomId']
    decision = True

    if (roomId in numClients.keys()):
        length = len(numClients[roomId])
        if (length >= 2):
            decision = False

    data['decision'] = decision
    
    sio.emit('grant_entry', data=data, to=sid)

@sio.event
def join_room(sid,message):
    roomId = message['roomId']
    userId = message['userId']
                
    sio.enter_room(sid,roomId)

    if (roomId not in numClients.keys()):
        numClients[roomId] = [userId]
    else:
        numClients[roomId].append(userId)

    sio.emit('user-connected', data={'userId':userId},room=roomId)

    @sio.event
    def message(sid, data):
        msg = data["message"]
        roomId = data["room"]
        sio.emit('createMessage', data={'message':msg},room=roomId,skip_sid=sid)

    @sio.event
    def disconnect(sid):
        sio.emit('user-disconnected', data={'userId':userId},room=roomId)

    @sio.event
    def leave(sid,message):
        roomId = message['roomId']
        url = '/join/left'
                    
        sio.leave_room(sid,roomId)

        if (roomId in numClients.keys()):
            if (userId in numClients[roomId]):
                numClients[roomId].remove(userId)
            if (len(numClients[roomId]) == 0):
                del numClients[roomId]

        sio.emit('user-left', room=roomId)
        sio.emit('user-disconnected', data={'userId':userId},room=roomId)
        sio.emit('redirect',{'url':url}, to=sid)

    @sio.event
    def initial_status(sid, data):
        sio.emit('detect-status', data=data,room=roomId,skip_sid=sid)

    @sio.event
    def toggle_video(sid, data):
        sio.emit('change_video_status', data=data,room=data['roomId'],skip_sid=sid)
    
    @sio.event
    def toggle_audio(sid, data):
        sio.emit('change_audio_status', data=data,room=data['roomId'],skip_sid=sid)    