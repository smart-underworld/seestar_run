import socket
import json
import time
from datetime import datetime
import threading
import sys
import argparse

class SeestarClient:
    def __init__(self, ip, port, cmdid):
        self.ip = ip
        self.port = port
        self.cmdid = cmdid
        self.is_watch_events = True

    def heartbeat(self): #I noticed a lot of pairs of test_connection followed by a get if nothing was going on
        self.json_message("test_connection")
    #    json_message("scope_get_equ_coord")

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
        self.socket = s
        return s

    def get_cmdid(self):
        cmdid = self.cmdid
        self.cmdid += 1
        return cmdid

    def get_op_state(self):
        return self.op_state

    def set_op_state(self, state):
        self.op_state = state

    def set_session_time(self, session_time):
        self.session_time = session_time

    def stop_watching(self):
        self.is_watch_events = False

    def send_message(self, data):
        try:
            self.socket.sendall(data.encode())  # TODO: would utf-8 or unicode_escaped help here
        except socket.error as e:
            self.connect()
            self.send_message(data)

    def get_socket_msg(self):
        try:
            data = self.socket.recv(1024 * 60)  # comet data is >50kb
        except socket.error as e:
            self.connect()
            data = self.socket.recv(1024 * 60)
        data = data.decode("utf-8")
        if is_debug:
            print("Received :", data)
        return data
        
    def receieve_message_thread_fn(self):
            
        msg_remainder = ""
        while self.is_watch_events:
            #print("checking for msg")
            data = self.get_socket_msg()
            if data:
                msg_remainder += data
                first_index = msg_remainder.find("\r\n")
                
                while first_index >= 0:
                    first_msg = msg_remainder[0:first_index]
                    msg_remainder = msg_remainder[first_index+2:]            
                    parsed_data = json.loads(first_msg)
                    
                    if 'Event' in parsed_data and parsed_data['Event'] == "AutoGoto":
                        state = parsed_data['state']
                        print("AutoGoto state: %s" % state)
                        if state == "complete" or state == "fail":
                            self.set_op_state(state)
                    
                    if is_debug:
                        print(parsed_data)
                        
                    first_index = msg_remainder.find("\r\n")
            time.sleep(1)

    def json_message(self, instruction):
        data = {"id": self.get_cmdid(), "method": instruction}
        json_data = json.dumps(data)
        if is_debug:
            print("Sending %s" % json_data)
        self.send_message(json_data+"\r\n")

    def json_message2(self, data):
        if data:
            json_data = json.dumps(data)
            if is_debug:
                print("Sending2 %s" % json_data)
            resp = self.send_message(json_data + "\r\n")


    def goto_target(self, ra, dec, target_name, is_lp_filter):
        print("going to target...")
        data = {}
        data['id'] = self.get_cmdid()
        data['method'] = 'iscope_start_view'
        params = {}
        params['mode'] = 'star'
        ra_dec = [ra, dec]
        params['target_ra_dec'] = ra_dec
        params['target_name'] = target_name
        params['lp_filter'] = is_lp_filter
        data['params'] = params
        self.json_message2(data)
        
    def start_stack(self):
        print("starting to stack...")
        data = {}
        data['id'] = self.get_cmdid()
        data['method'] = 'iscope_start_stack'
        params = {}
        params['restart'] = True
        data['params'] = params
        self.json_message2(data)

    def stop_stack(self):
        print("stop stacking...")
        data = {}
        data['id'] = self.get_cmdid()
        data['method'] = 'iscope_stop_view'
        params = {}
        params['stage'] = 'Stack'
        data['params'] = params
        self.json_message2(data)

    def wait_end_op(self):
        self.set_op_state('working')
        heartbeat_timer = 0
        while self.get_op_state() == "working":
            heartbeat_timer += 1
            if heartbeat_timer > 5:
                heartbeat_timer = 0
                self.json_message("test_connection")
            time.sleep(1)

        
    def sleep_with_heartbeat(self):
        stacking_timer = 0
        while stacking_timer < self.session_time:         # stacking time per segment
            stacking_timer += 1
            if stacking_timer % 5 == 0:
                self.json_message("test_connection")
            time.sleep(1)

def parse_ra_to_float(ra_string):
    # Split the RA string into hours, minutes, and seconds
    hours, minutes, seconds = map(float, ra_string.split(':'))

    # Convert to decimal degrees
    ra_decimal = hours + minutes / 60 + seconds / 3600

    return ra_decimal
    
def parse_dec_to_float(dec_string):
    # Split the Dec string into degrees, minutes, and seconds
    if dec_string[0] == '-':
        sign = -1
        dec_string = dec_string[1:]
    else:
        sign = 1
    print(dec_string)
    degrees, minutes, seconds = map(float, dec_string.split(':'))

    # Convert to decimal degrees
    dec_decimal = sign * (degrees + minutes / 60 + seconds / 3600)

    return dec_decimal
    
    
def main():
    global is_debug
    
    version_string = "1.0.0b1"
    print("seestar_run version: ", version_string)

    parser = setup_argparse()
    args = parser.parse_args()
    # This is a bit messy, but can be cleaned up in a future diff
    HOST = args.ip
    target_name = args.title
    center_RA = args.ra
    center_Dec = args.dec
    is_use_LP_filter = args.is_use_LP_filter
    session_time = args.session_time
    nRA = args.ra_panel_size
    nDec = args.dec_panel_size
    mRA = args.ra_offset_factor
    mDec = args.dec_offset_factor

    try:
        center_RA = float(center_RA)
    except ValueError:
        center_RA = parse_ra_to_float(center_RA)
        
    try:
        center_Dec = float(center_Dec)
    except ValueError:
        center_Dec = parse_dec_to_float(center_Dec)

    is_debug = args.is_debug == "Kai"

    print(HOST, target_name, center_RA, center_Dec, is_use_LP_filter, session_time, nRA, nDec, mRA, mDec)
    
    # verify mosaic pattern
    if nRA < 1 or nDec < 0:
        print("Mosaic size is invalid")
        sys.exit()
    
    print("nRA: %d", nRA)
    print("nDec:%d", nDec)
    
    PORT = 4700 
    cmdid = 999
    delta_RA = 0.06
    delta_Dec = 0.9

    seestar_client = SeestarClient(HOST, PORT, cmdid)
    seestar_client.set_session_time(session_time)
    s = seestar_client.connect()

    with s:
        
        # flush the socket input stream for garbage
        #get_socket_msg()
        
        if center_RA < 0:
            seestar_client.json_message("scope_get_equ_coord")
            data = seestar_client.get_socket_msg()
            parsed_data = json.loads(data)
            if parsed_data['method'] == "scope_get_equ_coord":
                data_result = parsed_data['result']
                center_RA = float(data_result['ra'])
                center_Dec = float(data_result['dec'])
                print(center_RA, center_Dec)
            
        # print input requests
        print("received parameters:")
        print("  ip address    : " + seestar_client.ip)
        print("  target        : " + target_name)
        print("  RA            : ", center_RA)
        print("  Dec           : ", center_Dec)
        print("  use LP filter : ", is_use_LP_filter)
        print("  session time  : ", seestar_client.session_time)
        print("  RA num panels : ", nRA)
        print("  Dec num panels: ", nDec)
        print("  RA offset x   : ", mRA)
        print("  Dec offset x  : ", mDec)
        
        delta_RA *= mRA
        delta_Dec *= mDec
        
        # adjust mosaic center if num panels is even
        if nRA % 2 == 0:
            center_RA += delta_RA/2
        if nDec % 2 == 0:
            center_Dec += delta_Dec/2
        
        get_msg_thread = threading.Thread(target=seestar_client.receieve_message_thread_fn)
        get_msg_thread.start()
        
        mosaic_index = 0
        cur_ra = center_RA-int(nRA/2)*delta_RA
        for index_ra in range(nRA):
            cur_dec = center_Dec-int(nDec/2)*delta_Dec
            for index_dec in range(nDec):
                if nRA == 1 and nDec == 1:
                    save_target_name = target_name
                else:
                    save_target_name = target_name+"_"+str(index_ra+1)+str(index_dec+1)
                print("goto ", (cur_ra, cur_dec))
                seestar_client.goto_target(cur_ra, cur_dec, save_target_name, is_use_LP_filter)
                seestar_client.wait_end_op()
                print("Goto operation finished")
                
                time.sleep(3)
                
                if seestar_client.get_op_state() == "complete":
                    seestar_client.start_stack()    
                    seestar_client.sleep_with_heartbeat()
                    seestar_client.stop_stack()
                    print("Stacking operation finished" + save_target_name)
                else:
                    print("Goto failed.")
                    
                cur_dec += delta_Dec
                mosaic_index += 1
            cur_ra += delta_RA
        
        
    print("Finished seestar_run")
    seestar_client.stop_watching()
    get_msg_thread.join(timeout=5)
    sys.exit()
    
    
def setup_argparse():
    parser = argparse.ArgumentParser(description='Seestar Run')
    parser.add_argument('ip', type=str,
                        help='Your SeeStar\'s IP address')
    parser.add_argument('title', type=str, help="Observation Target Title")
    parser.add_argument('ra', type=str, help="Right Ascenscion Target")
    parser.add_argument('dec', type=str, help="Declination Target")
    parser.add_argument('is_use_LP_filter', type=bool, help="Use the SeeStar's built-in light pollution filter.")
    parser.add_argument('session_time', type=int, help="Time (in seconds) for the stacking session")
    parser.add_argument('ra_panel_size', type=int, help="RA mosaic size")
    parser.add_argument('dec_panel_size', type=int, help="Dec mosaic size")
    parser.add_argument('ra_offset_factor', type=float)
    parser.add_argument('dec_offset_factor', type=float)
    parser.add_argument('is_debug', type=str, default=False, nargs='?', help="Print debug logs while running.")

    return parser
    

# seestar_run <ip_address> <target_name> <ra> <dec> <is_use_LP_filter> <session_time> <RA panel size> <Dec panel size> <RA offset factor> <Dec offset factor>
# python seestar_run.py 192.168.110.30 'Castor' '7:24:32.5' '-41:24:23.5' 0 60 2 2 1.0 1.0
# python seestar_run.py 192.168.110.30 'Castor' '7:24:32.5' '+41:24:23.5' 0 60 2 2 1.0 1.0
# python seestar_run.py 192.168.110.30 'Castor' '7:24:32.5' '41:24:23.5' 0 60 2 2 1.0 1.0
# python seestar_run.py 192.168.110.30 'Castor' 7.4090278 41.4065278 0 60 2 2 1.0 1.0
if __name__ == "__main__":
    main()
    

 
