# -*- coding: utf-8 -*-
"""
  _____      _       _           _____      _            _       _
 |  __ \    (_)     | |         / ____|    | |          | |     | |
 | |__) |__  _ _ __ | |_ ______| |     __ _| | ___ _   _| | __ _| |_ ___  _ __
 |  ___/ _ \| | '_ \| __|______| |    / _` | |/ __| | | | |/ _` | __/ _ \| '__|
 | |  | (_) | | | | | |_       | |___| (_| | | (__| |_| | | (_| | || (_) | |
 |_|   \___/|_|_| |_|\__|       \_____\__,_|_|\___|\__,_|_|\__,_|\__\___/|_|

Kave Point-Calculator : Python script for point calculation with viewers interactions
@version: 2.0.0
@author: V. / @Vinus
"""


# IMPORTS
import time
from datetime import datetime
import threading
import math
import keyboard
import requests
import queue
import json
import os
from urllib import request
from os.path import exists
from tkinter import *
from tkinter import ttk


# BEAUTIFUL PRINT CONSTANTS
BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BRIGHT_YELLOW ="\033[1;93m"
WHITE = "\033[1;97m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
NEGATIVE = "\033[7m"
CROSSED = "\033[9m"
END = "\033[0m"


# GET CONFIGS
config_filename = os.getcwd()+"\\src\\point-calc.config"
with open(config_filename, 'r') as config_file:
    config_json = json.loads(config_file.read())

# INPUTS
follower_filename = config_json['connection']['streamlabs']['folder'] + '\\' + config_json['connection']['streamlabs']['follower_filename']
sub_filename = config_json['connection']['streamlabs']['folder'] + '\\' + config_json['connection']['streamlabs']['sub_filename']
cheer_filename = config_json['connection']['streamlabs']['folder'] + '\\' + config_json['connection']['streamlabs']['cheer_filename']

request_client_id = config_json['connection']['twitch']['request_client_id']
request_client_secret = config_json['connection']['twitch']['request_client_secret']
request_twitch_oauth_url = config_json['connection']['twitch']['request_twitch_oauth_url']
request_twitch_stream_url = config_json['connection']['twitch']['request_twitch_stream_url']

request_patreon_url = config_json['connection']['patreon']['request_patreon_url']

sleep_time = config_json['connection']['request_interval']

# OUTPUTS
launch_time = datetime.now().isoformat()
console_verbose = config_json['output']['console']['verbose']
output_filename = config_json['output']['file']['folder'] + '\\' + config_json['output']['file']['filename']
log_filename = config_json['output']['log']['folder'] + '\\' + 'point-calc-' + launch_time.replace(':','-').replace('.','-') + '.log'

# POINT SCORES
follower_point_score = config_json['point_score']['follower']
sub_point_score = config_json['point_score']['sub']
cheer_point_score = config_json['point_score']['cheer']
view_point_score = config_json['point_score']['view']
patreon_point_score = config_json['point_score']['patreon']

# STARTING AMOUNTS
follower_starting_amount = config_json['starting_amount']['follower']
sub_starting_amount = config_json['starting_amount']['sub']
cheer_starting_amount = config_json['starting_amount']['cheer']
view_starting_amount = config_json['starting_amount']['view']
patreon_starting_amount = config_json['starting_amount']['patreon']

# THREAD TOOLS
thread_killer = False
point_queue = queue.Queue(1)

# VISUAL INTERFACE
point_label = Label()
window_width = config_json['output']['screen']['window_width']
window_height = config_json['output']['screen']['window_height']
font_size = config_json['output']['screen']['font_size']
interface_sleep_time = config_json['output']['screen']['update_interval'] * 1000


# CALCULATOR
def get_follower_amount():
    with open(follower_filename, 'r') as follower_file:
        follower_file_lines = follower_file.readlines()
    if(len(follower_file_lines)==0):
        return -1
    follower_amount = int(follower_file_lines[0])
    return follower_amount

def get_sub_amount():
    with open(sub_filename, 'r') as sub_file:
        sub_file_lines = sub_file.readlines()
    if(len(sub_file_lines)==0):
        return -1
    sub_amount = int(sub_file_lines[0])
    return sub_amount

def get_cheer_amount():
    with open(cheer_filename, 'r') as cheer_file:
        cheer_file_lines = cheer_file.readlines()
    if(len(cheer_file_lines)==0):
        return -1
    cheer_amount = int(cheer_file_lines[0])
    return cheer_amount

def get_view_amount():
    oauth_response = requests.post(
        request_twitch_oauth_url,
        data={'client_id':request_client_id, 'client_secret':request_client_secret, 'grant_type':'client_credentials'}
    )
    if(oauth_response.json()):
        bearer_token = oauth_response.json()["access_token"]

        stream_response = requests.get(
            request_twitch_stream_url,
            params={'user_login':'TWITCH USERNAME'}, #REPLACE BY YOUR TWITCH USERNAME
            headers={'Client-Id':request_client_id, 'Authorization':'Bearer '+bearer_token}
        )

        if(stream_response.json()["data"]):
            return stream_response.json()["data"][0]["viewer_count"]
        else:
            return 0

def get_patreon_amount():
    patreon_data = request.urlopen(request_patreon_url).read().decode("utf-8")
    patreon_json = json.loads(patreon_data)
    patreon_amount = len(patreon_json['PatronsList'])
    return patreon_amount

def back_worker():
    total_follower_gain = follower_starting_amount
    total_sub_gain = sub_starting_amount
    total_cheer_gain = cheer_starting_amount
    total_view_gain = view_starting_amount
    total_patreon_gain = patreon_starting_amount

    current_follower_amount = get_follower_amount()
    current_sub_amount = get_sub_amount()
    current_cheer_amount = get_cheer_amount()
    current_patreon_amount = get_patreon_amount()
    last_view_update = datetime.now().minute

    with open(log_filename, 'w') as log_file:
            log_json = {"exec_launch":launch_time, "point_score":{}, "starting_amount":{}, "logs":{}}
            log_json["point_score"]["follower"] = follower_point_score
            log_json["point_score"]["sub"] = sub_point_score
            log_json["point_score"]["cheer"] = cheer_point_score
            log_json["point_score"]["view"] = view_point_score
            log_json["point_score"]["patreon"] = patreon_point_score
            log_json["starting_amount"]["follower"] = follower_starting_amount
            log_json["starting_amount"]["sub"] = sub_starting_amount
            log_json["starting_amount"]["cheer"] = cheer_starting_amount
            log_json["starting_amount"]["view"] = view_starting_amount
            log_json["starting_amount"]["patreon"] = patreon_starting_amount
            log_file.write(json.dumps(log_json, indent=4))

    while(not thread_killer):
        temp_follower_amount = get_follower_amount()
        if(temp_follower_amount > current_follower_amount):
            total_follower_gain += temp_follower_amount - current_follower_amount
        current_follower_amount = temp_follower_amount

        temp_sub_amount = get_sub_amount()
        if(temp_sub_amount > current_sub_amount):
            total_sub_gain += temp_sub_amount - current_sub_amount
        current_sub_amount = temp_sub_amount

        temp_cheer_amount = get_cheer_amount()
        if(temp_cheer_amount > current_cheer_amount):
            total_cheer_gain += temp_cheer_amount - current_cheer_amount
        current_cheer_amount = temp_cheer_amount

        temp_view_amount = get_view_amount()
        temp_view_update = datetime.now().minute
        if(temp_view_update != last_view_update):
            total_view_gain += temp_view_amount
            last_view_update = temp_view_update

        temp_patreon_amount = get_patreon_amount()
        if(temp_patreon_amount > current_patreon_amount):
            total_patreon_gain += temp_patreon_amount - current_patreon_amount
        current_patreon_amount = temp_patreon_amount

        total_points_amount = math.ceil(total_follower_gain * follower_point_score
                                        + total_sub_gain * sub_point_score
                                        + total_cheer_gain * cheer_point_score
                                        + total_view_gain * view_point_score
                                        + total_patreon_gain * patreon_point_score)

        if(point_queue.full()):
            point_queue.get()
        point_queue.put(total_points_amount)

        if(console_verbose):
            printed_string_part1 = "\n\n---"
            printed_string_part2 = "\n>  Datetime : " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n>  Next update in " + str(sleep_time) + " seconds"
            printed_string_part3 = "\n\n>  Follower amount : " + str(total_follower_gain) + "\n>  Sub amount : " + str(total_sub_gain) + "\n>  Cheer amount : " + str(total_cheer_gain) + "\n>  View amount : " + str(total_view_gain) + "\n>  Patreon amount : " + str(total_patreon_gain)
            printed_string_part4 = "\n\nTotal points amount: " + str(total_points_amount)
            printed_string_part5 = "\n---"

            print(printed_string_part1 + printed_string_part2 + printed_string_part3 + BOLD + BRIGHT_YELLOW +  printed_string_part4 + END + printed_string_part5)

        with open(log_filename, 'r') as log_file:
            log_json = json.loads(log_file.read())
            log_time = datetime.now().isoformat()
            log_id = log_time.replace(':','').replace('.','').replace('-','').replace('T','')
            log_json["logs"][log_id] = {"timestamp":"","total_points_amount":0,"details":{}}
            log_json["logs"][log_id]["timestamp"] = log_time
            log_json["logs"][log_id]["total_points_amount"] = total_points_amount
            log_json["logs"][log_id]["details"]["follower_amount"] = str(total_follower_gain)
            log_json["logs"][log_id]["details"]["sub_amount"] = str(total_sub_gain)
            log_json["logs"][log_id]["details"]["cheer_amount"] = str(total_cheer_gain)
            log_json["logs"][log_id]["details"]["view_amount"] = str(total_view_gain)
            log_json["logs"][log_id]["details"]["patreon_amount"] = str(total_patreon_gain)
        
        with open(log_filename, 'w') as log_file:
            log_file.write(json.dumps(log_json, indent=4))

        with open(output_filename, 'w') as point_file:
            point_file.write(str(total_points_amount))

        time.sleep(sleep_time)


# INTERFACE
def interface_updater():
    global point_label
    if (not point_queue.empty()):
        point_label.config(text=str(point_queue.get()))
    point_label.after(interface_sleep_time, interface_updater)

def interface_creator():
    global point_label

    window = Tk()
    window.minsize(window_width, window_height)
    window.title("Kave Point Calculator v.2")
    window.configure(bg="#1d272a")
    window.iconbitmap(default=os.getcwd()+'/src/point.ico')


    point_label = Label(window, text=str("[init...]"), font=("Roboto", font_size), fg="#dfa549", bg="#1d272a")
    point_label.pack()

    interface_updater()

    window.mainloop()


# MAIN
def main():
    global thread_killer

    print(BOLD + BRIGHT_YELLOW + "\n\n  _____      _       _           _____      _            _       _             \n |  __ \    (_)     | |         / ____|    | |          | |     | |            \n | |__) |__  _ _ __ | |_ ______| |     __ _| | ___ _   _| | __ _| |_ ___  _ __ \n |  ___/ _ \| | '_ \| __|______| |    / _` | |/ __| | | | |/ _` | __/ _ \| '__|\n | |  | (_) | | | | | |_       | |___| (_| | | (__| |_| | | (_| | || (_) | |   \n |_|   \___/|_|_| |_|\__|       \_____\__,_|_|\___|\__,_|_|\__,_|\__\___/|_|  " + END)
    print("\Kave Point-Calculator : Python script for point calculation with viewers interactions\nby V. / @Vinus - (version 2.0.0)")
    print("\nFollower Point Score : " + str(follower_point_score) + "\nSubscription Point Score : " + str(sub_point_score) + "\nCheer Point Score : " + str(cheer_point_score) + "\nView Point Score : " + str(view_point_score) + "\nPatreon Point Score : " + str(patreon_point_score))
    print("\nTo quit, keep pressing \"suppr\"\n")

    back_worker_thread = threading.Thread(target=back_worker)
    back_worker_thread.start()

    interface_thread = threading.Thread(target=interface_creator)
    interface_thread.start()

    while(True):
        if(keyboard.is_pressed('suppr')):
            thread_killer = True
            break

    back_worker_thread.join()
    interface_thread.join()

    print("\n\nEND.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()