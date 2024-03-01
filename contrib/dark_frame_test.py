import socket
import os
import hashlib
import sys
import json
import time
from datetime import datetime
from ast import literal_eval
from flask import Flask, request, render_template

RTSPPORT = 1935
WEBPORT = 80
GUIDERPORT1 = 4030
GUIDERPORT2 = 4040
GUIDERPORT3 = 4400
GUIDERPORT4 = 4500
IMAGERPORT1 = 4700
IMAGERPORT2 = 4701
IMAGERPORT3 = 4800
IMAGERPORT4 = 4801
UPDATERPORT1 = 4350 #comms for cmds
UPDATERPORT2 = 4361 #accepts file upload

PORTS = [IMAGERPORT1,IMAGERPORT2,IMAGERPORT3,IMAGERPORT4,
         GUIDERPORT1,GUIDERPORT2,GUIDERPORT3,GUIDERPORT4,
         UPDATERPORT1,UPDATERPORT2]

HOST = '192.168.1.84'
PORT = PORTS[0]  # TODO: will this change based on target of JSON query, eg camera vs motors, etc? what about other ports?

global cmdid
global focuser_state_complete
global darklibrary_state_complete
global imaging_state_complete
global imaging_stage
global imaging_stage_state_complete
focuser_state_complete = False
darklibrary_state_complete = False
darklibrary_state_working = False
imaging_state_complete = False
imaging_stage = None
imaging_stage_state_complete = False
#TODO: Note that some of these routines will make available user-identifiable info such as latitude, longitude,
#   cpuid, license, timezone, time, serial number of unit, etc.
#TODO: not sure these are the best designed routine re handling variable size data returns
def listen_message(PORT): #TODO: not used? there's got to be a better way to monitor ports for msgs
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #for PORT in PORTS:
        if 1:
            s.connect((HOST, PORT))
            #s.listen(10)
            #print("Listening on %d ..."%PORT)
            #while 1:
            #    data = s.recv(1024 * 1)  # comet data is >50kb
            #    if data:
            #        parsed_data = json.loads(data)
            #        print(parsed_data)
            text = ''
            while True:
                chunk = s.recv(1024)
                text += chunk.decode()
                if not chunk or chunk.decode().endswith('\n'):
                    break
                print("Port: ", PORT, text)

def send_message(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data.encode())  # TODO: would utf-8 or unicode_escaped help here
        time.sleep(1)  # give it a moment to cough things up
        data = s.recv(1024 * 60)  # comet data is >50kb

    resp = repr(data)
    resp = resp.split("\\r\\n")
    if resp[-1] == "'":
        resp = resp[:-1]
    print("Received %s" % resp)
    return resp

def json_message(instruction):
    global cmdid
    cmdid += 1
    data = {"id": cmdid, "method": instruction}
    json_data = json.dumps(data)
    print("Sending %s" % json_data)

    resp = send_message(json_data+"\r\n")

    # return json_data #returned object is b'' of type string, but need to get rid of b\,
    # why doesnt str() or and encode/decode function work here??? dunno...
    print("%%%%%",resp[0])
    return resp[2:len(resp) - 5]  # this is a kludge and may not be foolproof?

def json_message2(data):
    if data:
        json_data = json.dumps(data)
        print("Sending %s" % json_data)

        resp = send_message(json_data + "\r\n")
        #resp = resp[2:len(resp) - 5] #TODO: fix this
        #return json.loads(resp)
        return resp

def heartbeat(): #I noticed a lot of pairs of test_connection followed by a get if nothing was going on
    #2 seconds goes by
    json_message("test_connection")
    #2 seconds goes by
    json_message("test_connection")
    #1 second goes by
    json_message("scope_get_equ_coord")

def get_socket_msg():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            data = s.recv(1024 * 60)  # comet data is >50kb
        except socket.error as e:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            data = s.recv(1024 * 60) #MattC
        data = data.decode("utf-8")
        if True:
            print("Received :", data)
        return data

'''
#figure out our local network ip address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IPAddr = s.getsockname()[0]
IPAddr = "127.0.0.1"

app = Flask(__name__)

#@app.route('/')
#def my_form():
#    return render_template('index.html')

@app.route('/', methods=['GET','POST'])
def home():
    global avar
    if request.method == 'GET':
        return render_template('index.html')

    avar = request.form['RA']
    myresults = [avar,avar]
    return render_template('index.html', results=myresults)

app.run(host=IPAddr, port='5000', debug=True) #'127.0.0.1'

quit()
'''

def startup_std():
    focuser_state_complete = False
    darklibrary_state_complete = False
    imaging_state_complete = False
    imaging_stage = None
    imaging_stage_state_complete = False
    json_message("pi_is_verified")
    # json_message("pi_shutdown")
    # quit()
    # cmdid += 1
    # json_message2({"id":cmdid,"method":"clear_app_state","params":{"name":"View"}})
    # json_message("get_app_state")
    cmdid += 1
    currentDateAndTime = datetime.now()
    json_message2({"id": cmdid, "method": "pi_set_time", "params": {"year": currentDateAndTime.year,
                                                                    "mon": currentDateAndTime.month,
                                                                    "day": currentDateAndTime.day,
                                                                    "hour": currentDateAndTime.hour,
                                                                    "min": currentDateAndTime.minute,
                                                                    "sec": currentDateAndTime.second,
                                                                    "time_zone": "Mars/Valinor_Hills"}})  # TODO: change this!
    ##CHECK:
    #json_message("scope_get_time")
    cmdid += 1
    #json_message2(
    #    {"id": cmdid, "method": "set_user_location", "params": {"lon": -22.999, "lat": 23.999}})  # TODO : change this!
    #cmdid += 1
    #json_message2({"id": cmdid, "method": "set_setting", "params": {"lang": "en"}})
    json_message("scope_get_equ_coord")
    json_message("scope_get_track_state")
    json_message("iscope_get_app_state")
    json_message("get_device_state")
    json_message("get_setting")
    json_message("get_stack_setting")

#find the json response in the case it and a number of "Event" packets are returned
def findjson(alistofresps):
    for akey in alistofresps:
        if 'jsonrpc' in akey:
            idx = alistofresps.index(akey)
            break
    return idx
def get_states():
    global focuser_state_complete
    global darklibrary_state_complete
    global darklibrary_state_working
    global imaging_state_complete
    global imaging_stage
    global imaging_stage_state_complete
    complete_states = ['complete','cancel','error','fail']

    aresp = json_message2({"id": cmdid, "method": "iscope_get_app_state", "params": {}})
    aresp2 = json.loads(aresp[findjson(aresp)][2:])
    # #these seem to reflect the states of the last effort, not necessarily an existing error state
    if 'FocuserMove' in aresp2['result'].keys():
        if aresp2['result']['FocuserMove']['state'] in complete_states:
            focuser_state_complete = True
            #focuser_state_success = True #TODO: should capture things like error, cancel, etc.
        else:
            print("FocuserMove:",aresp2['result']['FocuserMove']['state'])
    if 'DarkLibrary' in aresp2['result'].keys():
        if aresp2['result']['DarkLibrary']['state'] in complete_states:
            darklibrary_state_complete = True
            darklibrary_state_working = False
        else:
            darklibrary_state_complete = False
            darklibrary_state_working = True
            print("DarkLibrary:",aresp2['result']['DarkLibrary']['state'])
    if 'Imaging' in aresp2['result'].keys():
        if aresp2['result']['Imaging']['state'] in complete_states:
            imaging_state_complete = "True"
            imaging_stage = aresp2['result']['Imaging']['stage']
            if aresp2['result']['Imaging'][imaging_stage]['state'] in complete_states:
                imaging_stage_state_complete = True
            else:
                print("Imaging stage state status",aresp2['result']['Imaging'][imaging_stage]['state'])
        else:
            print("Imaging:",aresp2['result']['Imaging']['state'])
            imaging_stage = aresp2['result']['Imaging']['stage']
            print(" Imaging stage:",imaging_stage)
            print(" Imaging stage state status", aresp2['result']['Imaging'][imaging_stage]['state'])
    return

cmdid = 999 #I start this here so we reduce chance of stomping on an app command during testing; not sure if used

print("states at start")
get_states()
print(focuser_state_complete)
print(darklibrary_state_complete)
print(imaging_state_complete)
print(imaging_stage)
print(imaging_stage_state_complete)
print()

#try to clear things up for darkframe exposure
aresp = json_message("clear_autosave_err")
aresp = json_message("stop_exposure")
aresp = json_message("stop_create_dark") #not sure if this one is needed
aresp = json_message("stop_capture")

time.sleep(1)
#for info
aresp = json_message("get_camera_exp_and_bin")

needed_exposure = 3.322 #in seconds
aresp = json_message2({"id":cmdid,"method":"set_setting","params":{"exp_ms": {"stack_l":int(needed_exposure*1000),"continuous":500}}})
#check:
aresp = json_message("get_setting")

print("check after gets:")
get_states()
print(focuser_state_complete)
print(darklibrary_state_complete)
print(imaging_state_complete)
print(imaging_stage)
print(imaging_stage_state_complete)
print()

aresp = json_message2({"id":cmdid,"method":"start_create_dark","params":{"restart":True}}) #need restart?
aresp = json_message2({"id":cmdid,"method":"start_exposure","params":{"restart":True}})  #need restart?

print("start:")
get_states()
print(focuser_state_complete)
print(darklibrary_state_complete)
print(imaging_state_complete)
print(imaging_stage)
print(imaging_stage_state_complete)
print()

idx = 0
while darklibrary_state_working:
    get_states()
    idx += 1
    if idx % 1 == 0:
        print("checking:")
        print(focuser_state_complete)
        print(darklibrary_state_complete)
        print(imaging_state_complete)
        print(imaging_stage)
        print(imaging_stage_state_complete)
        print()
    time.sleep(1)

print("done:")
get_states()
print(focuser_state_complete)
print(darklibrary_state_complete)
print(imaging_state_complete)
print(imaging_stage)
print(imaging_stage_state_complete)
print()

aresp = json_message("stop_exposure")
aresp = json_message("stop_create_dark") #not sure if this one is needed
aresp = json_message("stop_capture")
aresp = json_message("clear_autosave_error")
aresp = json_message("get_device_state")
aresp = json_message("get_setting")

print("finished:")
get_states()
print(focuser_state_complete)
print(darklibrary_state_complete)
print(imaging_state_complete)
print(imaging_stage)
print(imaging_stage_state_complete)
print()

quit()
