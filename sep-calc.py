# -*- coding: utf-8 -*-
"""
   _____ ______ _____         _____      _      
  / ____|  ____|  __ \       / ____|    | |     
 | (___ | |__  | |__) |_____| |     __ _| | ___ 
  \___ \|  __| |  ___/______| |    / _` | |/ __|
  ____) | |____| |          | |___| (_| | | (__ 
 |_____/|______|_|           \_____\__,_|_|\___|
                                                
SEP-Calc : StreamEventPoint Calculator python script
- Get log informations
- Return point total amount
@version: 1.0.0
@author: V. / @Vinus
"""


# IMPORTS
from threading import Thread
from supabase import create_client
import math
import keyboard
import time
import os
import json


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

# POINT SCORES
follower_point_score: int = config_json['point_score']['follower']
sub_point_score: int = config_json['point_score']['sub']
cheer_point_score: int = config_json['point_score']['cheer']
view_point_score: int = config_json['point_score']['view']
patreontier1_point_score: int = config_json['point_score']['patreon_tier1']
patreontier2_point_score: int = config_json['point_score']['patreon_tier2']
patreontier3_point_score: int = config_json['point_score']['patreon_tier3']

# THREAD TOOLS
thread_killer: bool = False
sleep_time: int = config_json['connection']['request_interval']


# GET NUMBER SUM
def get_number_sum(logs_list: list[dict]) -> int:
    sum = 0
    for log in logs_list:
        sum += log["number"]
    return sum

# TOTAL POINT AMOUNT CALCULATOR
def total_points_calculator() -> int:
    follow_number: int = len(supabase.table("logs").select("rank, type, number").eq("type","TWITCH_FOLLOW").execute().data)
    sub_number: int = len(supabase.table("logs").select("rank, type, number").eq("type","TWITCH_SUB").execute().data)
    view_number: int = get_number_sum(supabase.table("logs").select("rank, type, number").eq("type","TWITCH_VIEW").execute().data)
    cheer_number: int = get_number_sum(supabase.table("logs").select("rank, type, number").eq("type","TWITCH_CHEER").execute().data)
    patreontier1_number: int = len(supabase.table("logs").select("rank, type, number").eq("type","PATREON_TIER1").execute().data)
    patreontier2_number: int = len(supabase.table("logs").select("rank, type, number").eq("type","PATREON_TIER2").execute().data)
    patreontier3_number: int = len(supabase.table("logs").select("rank, type, number").eq("type","PATREON_TIER3").execute().data)

    total_points_amount: int = math.ceil(follow_number * follower_point_score
                                        + sub_number * sub_point_score
                                        + cheer_number * cheer_point_score
                                        + view_number * view_point_score
                                        + patreontier1_number * patreontier1_point_score
                                        + patreontier2_number * patreontier2_point_score
                                        + patreontier3_number * patreontier3_point_score)
    
    return total_points_amount


# SEP-CALCULATOR
def sep_calulator() -> None:
    while(not thread_killer):
        total_points_amount:int = total_points_calculator()
        supabase.table("point-total").insert({"point_total":total_points_amount}).execute()

        time.sleep(sleep_time)


# MAIN
def main():
    global thread_killer
    
    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____         _____      _      \n  / ____|  ____|  __ \       / ____|    | |     \n | (___ | |__  | |__) |_____| |     __ _| | ___ \n  \___ \|  __| |  ___/______| |    / _` | |/ __|\n  ____) | |____| |          | |___| (_| | | (__ \n |_____/|______|_|           \_____\__,_|_|\___|" + END)
    print("\nSEP-Calc : StreamEventPoint Calculator python script\nby V. / @Vinus - (version 1.0.0)")
    print(ITALIC + DARK_GRAY + "\nFollower Point Score : " + str(follower_point_score) + "\nSubscription Point Score : " + str(sub_point_score) + "\nCheer Point Score : " + str(cheer_point_score) + "\nView Point Score : " + str(view_point_score) + "\nPatreon Tier1 Point Score : " + str(patreontier1_point_score) + "\nPatreon Tier2 Point Score : " + str(patreontier2_point_score) + "\nPatreon Tier3 Point Score : " + str(patreontier3_point_score) + END)
    print("\nTo quit, keep pressing \"suppr\"\n")

    sep_calculator_thread = Thread(target=sep_calulator)
    sep_calculator_thread.start()

    while(True):
        if(keyboard.is_pressed('suppr')):
            thread_killer = False#True
            break

    sep_calculator_thread.join()

    print("END.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()