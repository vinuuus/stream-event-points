# -*- coding: utf-8 -*-
"""
   _____ ______ _____        _           _          _ 
  / ____|  ____|  __ \      | |         | |        | |
 | (___ | |__  | |__) |_____| |     __ _| |__   ___| |
  \___ \|  __| |  ___/______| |    / _` | '_ \ / _ \ |
  ____) | |____| |          | |___| (_| | |_) |  __/ |
 |_____/|______|_|          |______\__,_|_.__/ \___|_|
                                                      
SEP-Label : StreamEventPoint Label python script
- Get unlabeled twitch_sub logs
- Label twitch_sub logs
@version: 1.0.0
@author: V. / @Vinus
"""


# IMPORTS
from supabase import create_client
import time
import os
import json
import keyboard
from datetime import datetime


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
sleep_time: int = config_json['connection']['request_interval']


# MAIN
def main():
    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____        _           _          _ \n  / ____|  ____|  __ \      | |         | |        | |\n | (___ | |__  | |__) |_____| |     __ _| |__   ___| |\n  \___ \|  __| |  ___/______| |    / _` | '_ \ / _ \ |\n  ____) | |____| |          | |___| (_| | |_) |  __/ |\n |_____/|______|_|          |______\__,_|_.__/ \___|_|" + END)
    print("\nSEP-Label : StreamEventPoint Label python script\nby V. / @Vinus - (version 1.0.0)")
    print("\nTo quit, type \"quit\" or keep pressing \"suppr\"\n")

    killer: bool = False
    waiter: bool = True
    while(True):
        unlabeled_logs: list = supabase.table("logs").select("id, rank, created_at, type, name").is_("name", "null").eq("type","TWITCH_SUB").execute().data
        for log in unlabeled_logs:
            waiter = True

            log_datetime: datetime = datetime.fromisoformat(log["created_at"])
            print(END + "\n> " + CYAN + BOLD + log_datetime.strftime("%H:%M:%S") + " - " + END + CYAN + "[" + str(log["rank"]) + "] " + log["id"] + END)
            input_text = input("   => " + LIGHT_RED + ITALIC)

            if input_text == "quit":
                killer = True
                break
            supabase.table("logs").update({"name":input_text}).eq("id",log["id"]).execute()

        if killer == True or keyboard.is_pressed('suppr'):
            break

        if waiter:
            print(END + "\ngetting unlabeled sub logs ...")
            waiter = False
        time.sleep(sleep_time)

    print(END + "\nEND.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()