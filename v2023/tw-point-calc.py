# -*- coding: utf-8 -*-
"""
  _____      _       _           _____      _            _       _
 |  __ \    (_)     | |         / ____|    | |          | |     | |
 | |__) |__  _ _ __ | |_ ______| |     __ _| | ___ _   _| | __ _| |_ ___  _ __
 |  ___/ _ \| | '_ \| __|______| |    / _` | |/ __| | | | |/ _` | __/ _ \| '__|
 | |  | (_) | | | | | |_       | |___| (_| | | (__| |_| | | (_| | || (_) | |
 |_|   \___/|_|_| |_|\__|       \_____\__,_|_|\___|\__,_|_|\__,_|\__\___/|_|

POINT-CALCULATOR : Python script for point calculation with viewers interactions
@version: 1.1.0
@author: V. / @Vinus
"""

import time
from datetime import datetime
import threading
import math
import keyboard
import requests
import queue
from tkinter import *
from tkinter import ttk


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


streamlabels_folder = "C:\\Users\\"

follower_filename = "session_follower_count.txt"
sub_filename = "session_subscriber_score.txt"
cheer_filename = "session_cheer_amount.txt"

point_filename = "session_point_amount.txt"

log_filename = "point-goal.log"

request_client_id = ""
request_client_secret = ""
request_twitch_oauth_url = "https://id.twitch.tv/oauth2/token"
request_twitch_stream_url = "https://api.twitch.tv/helix/streams"
twitch_username = 'username'

request_utip_balance_url = ""

follower_point_score = 500
sub_point_score = 100
cheer_point_score = 1
view_point_score = 2
tip_point_score = 100

sleep_time = 5

thread_killer = False

point_queue = queue.Queue(1)

point_label = Label()
window_width = 700
window_height = 200
interface_sleep_time = 1000


def get_follower_amount():
    follower_file = open(streamlabels_folder + follower_filename, "r")
    follower_amount = int(follower_file.readlines()[0])
    follower_file.close()
    return follower_amount

def get_sub_amount():
    sub_file = open(streamlabels_folder + sub_filename, "r")
    sub_amount = int(sub_file.readlines()[0])
    sub_file.close()
    return sub_amount

def get_cheer_amount():
    cheer_file = open(streamlabels_folder + cheer_filename, "r")
    cheer_amount = int(cheer_file.readlines()[0])
    cheer_file.close()
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
            params={'user_login':twitch_username},
            headers={'Client-Id':request_client_id, 'Authorization':'Bearer '+bearer_token}
        )

        if(stream_response.json()["data"]):
            return stream_response.json()["data"][0]["viewer_count"]
        else:
            return 0

def get_tip_amount():
    tip_response = requests.get(request_utip_balance_url, stream=True)
    line_number = 0
    for line in tip_response.iter_lines():
        line_number+=1
        if line and line_number == 5:
            return(float(line.decode('utf-8')[6:-2].replace(',','.')))

def back_worker():
    total_follower_gain = 4
    total_sub_gain = 83
    total_cheer_gain = 10
    total_view_gain = 18000
    total_tip_gain = 0

    current_follower_amount = get_follower_amount()
    current_sub_amount = get_sub_amount()
    current_cheer_amount = get_cheer_amount()
    current_tip_amount = get_tip_amount()
    last_view_update = datetime.now().minute

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

        temp_tip_amount = get_tip_amount()
        if(temp_tip_amount > current_tip_amount):
            total_tip_gain += temp_tip_amount - current_tip_amount
        current_tip_amount = temp_tip_amount

        total_points_amount = math.ceil(total_follower_gain * follower_point_score
                                        + total_sub_gain * sub_point_score
                                        + total_cheer_gain * cheer_point_score
                                        + total_view_gain * view_point_score
                                        + total_tip_gain * tip_point_score)

        if(point_queue.full()):
            point_queue.get()
        point_queue.put(total_points_amount)

        printed_string_part1 = "\n\n---"
        printed_string_part2 = "\n>  Datetime : " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n>  Next update in " + str(sleep_time) + " seconds"
        printed_string_part3 = "\n\n>  Follower amount : " + str(total_follower_gain) + "\n>  Sub amount : " + str(total_sub_gain) + "\n>  Cheer amount : " + str(total_cheer_gain) + "\n>  View amount : " + str(total_view_gain) + "\n>  Tip amount : " + str(total_tip_gain)
        printed_string_part4 = "\n\nTotal points amount: " + str(total_points_amount)
        printed_string_part5 = "\n---"

        print(printed_string_part1 + printed_string_part2 + printed_string_part3 + BOLD + BRIGHT_YELLOW +  printed_string_part4 + END + printed_string_part5)

        with open(log_filename, 'a') as log_file:
            log_file.write("\n\n" + printed_string_part1 + printed_string_part2 + printed_string_part3 + printed_string_part4)

        with open(streamlabels_folder + point_filename, 'w') as point_file:
            point_file.write(str(total_points_amount))

        time.sleep(sleep_time)


def interface_updater():
    global point_label
    if (not point_queue.empty()):
        point_label.config(text=str(point_queue.get()))
    point_label.after(interface_sleep_time, interface_updater)

def interface_creator():
    global point_label

    window = Tk()
    window.minsize(window_width, window_height)
    window.title("Twitch Point Calculator")
    window.configure(bg="#1d272a")

    point_label = Label(window, text=str("[init...]"), font=("Roboto", 150), fg="#dfa549", bg="#1d272a")
    point_label.pack()

    interface_updater()

    window.mainloop()


def main():
    global thread_killer

    print(BOLD + BRIGHT_YELLOW + "\n\n  _____      _       _           _____      _            _       _             \n |  __ \    (_)     | |         / ____|    | |          | |     | |            \n | |__) |__  _ _ __ | |_ ______| |     __ _| | ___ _   _| | __ _| |_ ___  _ __ \n |  ___/ _ \| | '_ \| __|______| |    / _` | |/ __| | | | |/ _` | __/ _ \| '__|\n | |  | (_) | | | | | |_       | |___| (_| | | (__| |_| | | (_| | || (_) | |   \n |_|   \___/|_|_| |_|\__|       \_____\__,_|_|\___|\__,_|_|\__,_|\__\___/|_|  " + END)
    print("\nPOINT-CALCULATOR : Python script for point calculation with viewers interactions\nby V. / @Vinus - (version 1.1.0)")
    print("\nStreamlabels folder : " + ITALIC + streamlabels_folder + END + "\n |-> Follower Streamlabels Filename : " + ITALIC + follower_filename + END + "\n |-> Subscription Streamlabels Filename : " + ITALIC + sub_filename + END + "\n |-> Cheer Streamlabels Filename : " + ITALIC + cheer_filename + END)
    print("Twitch client_id = " + ITALIC + request_client_id + END)
    print("Utip balance URL = " + ITALIC + request_utip_balance_url + END)
    print("\nFollower Point Score : " + str(follower_point_score) + "\nSubscription Point Score : " + str(sub_point_score) + "\nCheer Point Score : " + str(cheer_point_score) + "\nView Point Score : " + str(view_point_score) + "\nTip Point Score : " + str(tip_point_score))
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



#execute main ssi le script a ete appele directement
#(ne s execute pas si integre dans un autre fichier)
if __name__ == "__main__":
    main()
