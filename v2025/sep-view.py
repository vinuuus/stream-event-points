# -*- coding: utf-8 -*-
"""
   _____ ______ _____     __      ___               
  / ____|  ____|  __ \    \ \    / (_)              
 | (___ | |__  | |__) |____\ \  / / _  _____      __
  \___ \|  __| |  ___/______\ \/ / | |/ _ \ \ /\ / /
  ____) | |____| |           \  /  | |  __/\ V  V / 
 |_____/|______|_|            \/   |_|\___| \_/\_/  
                                                    
SEP-View : StreamEventPoint Viewers python script
- Get active viewers informations
- Update active viewers informations
@version: 1.0.0
@author: V. / @Vinus
"""


# IMPORTS
from threading import Thread
from supabase import create_client
import keyboard
import os
import json
from socket import socket
from datetime import datetime, timezone, timedelta


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
config_filename = os.getcwd()+"\\src\\sep.config"
with open(config_filename, 'r') as config_file:
    config_json = json.loads(config_file.read())

# SUPABASE CONNECTIONS
supabase_url: str = config_json['connection']['supabase']['request_url']
supabase_key: str = config_json['connection']['supabase']['request_key']
supabase = create_client(supabase_url, supabase_key)

# TWITCH IRC CONNECTIONS
twitch_irc_host: str = "irc.twitch.tv"
twitch_irc_port: int = 6667
twitch_irc_channel: str = "lakavelive"
twitch_irc_pass: str = "oauth:z6rg29379jb2upjglwfku8tlrzweup"
twitch_irc_nick: str = "maitretimonier"
irc_socket = socket()
irc_socket.connect((twitch_irc_host, twitch_irc_port))

# ACTIVE CHAT PARAMETERS
chat_active_time: int = config_json['awarding']['chat_active_time']

# THREAD TOOLS
thread_killer: bool = False
sleep_time: int = config_json['connection']['request_interval']


# SEP-RANDOM
def sep_viewers() -> None:
    readbuffer: list = []

    irc_socket.send(("PASS " + twitch_irc_pass + "\r\n").encode('utf-8'))
    irc_socket.send(("NICK " + twitch_irc_nick + "\r\n").encode('utf-8'))
    irc_socket.send(("JOIN #" + twitch_irc_channel + " \r\n").encode('utf-8'))

    while(not thread_killer):
        received = irc_socket.recv(1024).decode('utf-8').split("\n")
        readbuffer.extend(received)
        
        for line in readbuffer:
            if (line.split(" ")[0] == "PING"):
                irc_socket.send(("PONG %s\r\n" % line[1]).encode('utf-8'))
            elif (len(line) > 1 and line.split(" ")[1] == "PRIVMSG"):
                pseudo: str = line.split("!")[0][1:]
                viewers: list = supabase.table("viewers").select("name").eq("active",True).execute().data
                viewers_list: list[str] = [viewer["name"] for viewer in viewers]
                if pseudo in viewers_list:
                    supabase.table("viewers").update({"last_update":datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f+00"),"active":True}).eq("name",pseudo).execute()
                else:
                    supabase.table("viewers").insert({"name":pseudo}).execute()
                supabase.table("viewers").update({"active":False}).eq("active",True).lt("last_update",(datetime.now(timezone.utc)-timedelta(minutes=chat_active_time)).strftime("%Y-%m-%d %H:%M:%S.%f+00")).execute()

        readbuffer.clear()


# MAIN
def main():
    global thread_killer
    
    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____     __      ___               \n  / ____|  ____|  __ \    \ \    / (_)              \n | (___ | |__  | |__) |____\ \  / / _  _____      __\n  \___ \|  __| |  ___/______\ \/ / | |/ _ \ \ /\ / /\n  ____) | |____| |           \  /  | |  __/\ V  V / \n |_____/|______|_|            \/   |_|\___| \_/\_/  " + END)
    print("\nSEP-View : StreamEventPoint Viewers python script\nby V. / @Vinus - (version 1.0.0)")
    print("\nTo quit, keep pressing \"suppr\"\n")

    sep_viewers_thread = Thread(target=sep_viewers)
    sep_viewers_thread.start()

    while(True):
        if(keyboard.is_pressed('suppr')):
            thread_killer = False#True
            break

    sep_viewers_thread.join()

    print("END.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()