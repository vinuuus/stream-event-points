# -*- coding: utf-8 -*-
"""
   _____ ______ _____        _____                 _ 
  / ____|  ____|  __ \      |  __ \               | |
 | (___ | |__  | |__) |_____| |__) |__ _ _ __   __| |
  \___ \|  __| |  ___/______|  _  // _` | '_ \ / _` |
  ____) | |____| |          | | \ \ (_| | | | | (_| |
 |_____/|______|_|          |_|  \_\__,_|_| |_|\__,_|
                                                     
SEP-Rand : StreamEventPoint Random python script
- Get log informations
- Get point informations
- Return case awardings
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
import random


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

# AWARDING PARAMETERS
random_excluded_viewers: list[str] = config_json['awarding']['random_excluded_viewers']

# THREAD TOOLS
thread_killer: bool = False
sleep_time: int = config_json['connection']['request_interval']


# GET RANDOM VIEWER
def get_random_viewer() -> str:
    active_viewers: list = supabase.table("viewers").select("name").eq("active",True).execute().data
    active_viewers_list: list[str] = [viewer["name"] for viewer in active_viewers]
    for excluded_viewer in random_excluded_viewers:
        if excluded_viewer in active_viewers_list:
            active_viewers_list.remove(excluded_viewer)
    if(len(active_viewers_list)>0):
        return random.choice(active_viewers_list)
    else:
        return "pyratt_"

# AWARD POINT STAGES LOGS TO A RANDOM VIEWER
def name_point_stages() -> None:
    unnamed_point_stages: list = supabase.table("logs").select("rank, type, name, counted").is_("name", "null").eq("type","POINT_STAGE").execute().data
    for point_stage in unnamed_point_stages:
        supabase.table("logs").update({"name":get_random_viewer() + " (aleatoire)"}).eq("rank",point_stage["rank"]).execute()

# AWARD CASE TO LOGS
def award_logs() -> None:
    unawarded_logs: list = supabase.table("logs").select("id, rank, type, name, counted").not_.is_("name", "null").eq("counted",False).in_("type",["TWITCH_SUB", "PATREON_TIER1", "PATREON_TIER2", "PATREON_TIER3", "POINT_STAGE"]).execute().data
    for log in unawarded_logs:
        unopened_cases: list = supabase.table("grid").select("id, winner, opened").eq("opened",False).eq("winner","").execute().data
        awarded_case_id = random.choice(unopened_cases)["id"]
        supabase.table("grid").update({"winner":log["name"],"opened":True}).eq("id",awarded_case_id).execute()
        if log["type"] == "PATREON_TIER3":
            unopened_cases: list = supabase.table("grid").select("id, winner, opened").eq("opened",False).eq("winner","").execute().data
            awarded_case_id = random.choice(unopened_cases)["id"]
            supabase.table("grid").update({"winner":log["name"],"opened":True}).eq("id",awarded_case_id).execute()
        supabase.table("logs").update({"counted":True}).eq("id",log["id"]).execute()

# SEP-RANDOM
def sep_random() -> None:
    while(not thread_killer):
        name_point_stages()
        award_logs()
        
        time.sleep(sleep_time)


# MAIN
def main():
    global thread_killer
    
    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____        _____                 _ \n  / ____|  ____|  __ \      |  __ \               | |\n | (___ | |__  | |__) |_____| |__) |__ _ _ __   __| |\n  \___ \|  __| |  ___/______|  _  // _` | '_ \ / _` |\n  ____) | |____| |          | | \ \ (_| | | | | (_| |\n |_____/|______|_|          |_|  \_\__,_|_| |_|\__,_|" + END)
    print("\nSEP-Rand : StreamEventPoint Random python script\nby V. / @Vinus - (version 1.0.0)")
    print("\nTo quit, keep pressing \"suppr\"\n")

    sep_random_thread = Thread(target=sep_random)
    sep_random_thread.start()

    while(True):
        if(keyboard.is_pressed('suppr')):
            thread_killer = False#True
            break

    sep_random_thread.join()

    print("END.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()