# -*- coding: utf-8 -*-
"""
   _____ ______ _____        _____      _       _   
  / ____|  ____|  __ \      |  __ \    (_)     | |  
 | (___ | |__  | |__) |_____| |__) | __ _ _ __ | |_ 
  \___ \|  __| |  ___/______|  ___/ '__| | '_ \| __|
  ____) | |____| |          | |   | |  | | | | | |_ 
 |_____/|______|_|          |_|   |_|  |_|_| |_|\__|
                                                    
SEP-Print : StreamEventPoint Print python script
- Get case informations
- Print case awardings in chat
@version: 1.0.0
@author: V. / @Vinus
"""


# IMPORTS
from threading import Thread
from supabase import create_client
import keyboard
import time
import os
import json
from socket import socket


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

# THREAD TOOLS
thread_killer: bool = False
sleep_time: int = config_json['connection']['request_interval']


# PING PONG
def ping_handler() -> None:
    readbuffer: list = []
    while(not thread_killer):
        received = irc_socket.recv(1024).decode('utf-8').split("\n")
        readbuffer.extend(received)
        
        for line in readbuffer:
            if (line.split(" ")[0] == "PING"):
                irc_socket.send(("PONG %s\r\n" % line[1]).encode('utf-8'))

        readbuffer.clear()

# PRINT TOTAL POINTS AMOUNT IN FILE
def sep_print() -> None:
    while(not thread_killer):
        unprinted_opened_cases: list = supabase.table("grid").select("id, type, infos, winner, opened, printed").eq("opened",True).eq("printed",False).neq("winner","").execute().data
        for case in unprinted_opened_cases:
            if case["infos"] != "":
                irc_socket.send(("PRIVMSG #" + twitch_irc_channel + " :" + "La case n°" + str(case["id"]) + " a été ouverte par " + case["winner"] + " : " + case["type"] + " (" + case["infos"] + ")" "\r\n").encode('utf-8'))
            else:
                irc_socket.send(("PRIVMSG #" + twitch_irc_channel + " :" + "La case n°" + str(case["id"]) + " a été ouverte par " + case["winner"] + " : " + case["type"] + "\r\n").encode('utf-8'))
            supabase.table("grid").update({"printed":True}).eq("id",case["id"]).execute()
        time.sleep(sleep_time)


# MAIN
def main():
    global thread_killer

    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____        _____      _       _   \n  / ____|  ____|  __ \      |  __ \    (_)     | |  \n | (___ | |__  | |__) |_____| |__) | __ _ _ __ | |_ \n  \___ \|  __| |  ___/______|  ___/ '__| | '_ \| __|\n  ____) | |____| |          | |   | |  | | | | | |_ \n |_____/|______|_|          |_|   |_|  |_|_| |_|\__|" + END)
    print("\nSEP-Print : StreamEventPoint Print python script\nby V. / @Vinus - (version 1.0.0)")
    print("\nTo quit, keep pressing \"suppr\"\n")

    irc_socket.send(("PASS " + twitch_irc_pass + "\r\n").encode('utf-8'))
    irc_socket.send(("NICK " + twitch_irc_nick + "\r\n").encode('utf-8'))
    irc_socket.send(("JOIN #" + twitch_irc_channel + " \r\n").encode('utf-8'))

    ping_handler_thread = Thread(target=ping_handler)
    ping_handler_thread.start()

    sep_print_thread = Thread(target=sep_print)
    sep_print_thread.start()

    while(True):
        if(keyboard.is_pressed('suppr')):
            thread_killer = False#True
            break

    ping_handler_thread.join()
    sep_print_thread.join()

    print("END.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()