# -*- coding: utf-8 -*-
"""
   _____ ______ _____        _                 
  / ____|  ____|  __ \      | |                
 | (___ | |__  | |__) |_____| |     ___   __ _ 
  \___ \|  __| |  ___/______| |    / _ \ / _` |
  ____) | |____| |          | |___| (_) | (_| |
 |_____/|______|_|          |______\___/ \__, |
                                          __/ |
                                         |___/ 
                                               
SEP-Log : StreamEventPoint Log python script
- Get Patreon informations
- Get Twitch informations
- Return log informations
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
import requests
import patreon
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

# TWITCH API CONNECTIONS
twitch_api_client_id: str = config_json['connection']['twitch_api']['client_id']
twitch_api_client_secret: str = config_json['connection']['twitch_api']['client_secret']
twitch_api_oauth_request_url: str = config_json['connection']['twitch_api']['oauth_request_url']
twitch_api_streams_request_url: str = config_json['connection']['twitch_api']['streams_request_url']

# STREAMLABELS CONNECTIONS
streamlabels_follower_filename: str = config_json['connection']['streamlabels']['folder'] + '\\' + config_json['connection']['streamlabels']['follower_filename']
streamlabels_sub_filename: str = config_json['connection']['streamlabels']['folder'] + '\\' + config_json['connection']['streamlabels']['sub_filename']
streamlabels_cheer_filename: str = config_json['connection']['streamlabels']['folder'] + '\\' + config_json['connection']['streamlabels']['cheer_filename']

# PATREON CONNECTIONS
patreon_client_id: str = config_json['connection']['patreon']['client_id']
patreon_client_secret: str = config_json['connection']['patreon']['client_secret']
patreon_creator_id: str = config_json['connection']['patreon']['creator_id']
api_client = patreon.API(patreon_creator_id)
patreon_tier1_name: str = config_json['connection']['patreon']['tier1_name']
patreon_tier2_name: str = config_json['connection']['patreon']['tier2_name']
patreon_tier3_name: str = config_json['connection']['patreon']['tier3_name']
previous_memberships_count: dict = {patreon_tier1_name:0,patreon_tier2_name:3,patreon_tier3_name:1}

# THREAD TOOLS
thread_killer: bool = False
sleep_time: int = config_json['connection']['request_interval']


# ADD POINT STAGES LOGS
def add_point_stages_logs() -> None:
    old_stages_amount: int = len(supabase.table("logs").select("rank, type, number").eq("type","POINT_STAGE").execute().data)
    total_points_amount: int = supabase.table("point-total").select("rank, point_total").order("rank", desc=False).execute().data[-1]["point_total"]
    to_add_stages_amount: int = max(0,(total_points_amount//1000)-old_stages_amount)

    for i in range(to_add_stages_amount):
        supabase.table("logs").insert({"type":"POINT_STAGE"}).execute()

# ADD PATREON LOGS
def add_patreon_logs() -> None:
    global previous_memberships_count

    #get all memberships count
    memberships_count = {}
    attributes = api_client.fetch_campaign().json_data['included']
    for attribute in attributes:
        try:
            membership = attribute['attributes']
            if(membership['amount']) != 0:
                memberships_count[membership['title']] = membership['patron_count']
        except:
            pass

    #get amount of new membership for every tier
    new_memberships_count = {}
    new_memberships: int = 0
    for membership in memberships_count.keys():
        new_memberships_count[membership] = memberships_count[membership] - previous_memberships_count[membership]
        previous_memberships_count[membership] = memberships_count[membership]
        new_memberships = new_memberships + memberships_count[membership]

    if new_memberships > 0:
        #get all patrons
        campaign_id: str = api_client.fetch_campaign().data()[0].id()
        pledges_response = api_client.fetch_page_of_pledges(campaign_id,25,)
        patrons_list: list = []
        all_pledges = pledges_response.data()
        for pledge in all_pledges:
            patron_id: str = pledge.relationship('patron').id()
            patron = api_client.fetch_campaign_and_patrons().find_resource_by_type_and_id('user',patron_id)
            patrons_list.append(patron.attribute('full_name'))

        #get rid of old patrons
        patreon_logs: list = supabase.table("logs").select("id, type, name").not_.is_("name", "null").in_("type",["PATREON_TIER1", "PATREON_TIER2", "PATREON_TIER3"]).execute().data
        old_patron_list: list[str] = [log["name"] for log in patreon_logs]
        for patron in old_patron_list:
            patron_name = patron.split(" ")[0]
            if (patron_name) in patrons_list:
                patrons_list.remove(patron_name)
        
        #add patreon logs
        for patron in patrons_list:
            if(new_memberships_count[patreon_tier3_name] != 0):
                supabase.table("logs").insert({"type":"PATREON_TIER3","name":patron+" (Patreon)"}).execute()
            elif(new_memberships_count[patreon_tier2_name] != 0):
                supabase.table("logs").insert({"type":"PATREON_TIER2","name":patron+" (Patreon)"}).execute()
            elif(new_memberships_count[patreon_tier1_name] != 0):
                supabase.table("logs").insert({"type":"PATREON_TIER1","name":patron+" (Patreon)"}).execute()

# GET TWITCH FOLLOW AMOUNT
def get_twitch_follow_amount() -> int:
    with open(streamlabels_follower_filename, 'r') as follower_file:
        follower_file_lines = follower_file.readlines()
    if(len(follower_file_lines)==0):
        return -1
    follower_amount = int(follower_file_lines[0])
    return follower_amount

# GET TWITCH SUB AMOUNT
def get_twitch_sub_amount() -> int:
    with open(streamlabels_sub_filename, 'r') as sub_file:
        sub_file_lines = sub_file.readlines()
    if(len(sub_file_lines)==0):
        return -1
    sub_amount = int(sub_file_lines[0])
    return sub_amount

# GET TWITCH CHEER AMOUNT
def get_twitch_cheer_amount() -> int:
    with open(streamlabels_cheer_filename, 'r') as cheer_file:
        cheer_file_lines = cheer_file.readlines()
    if(len(cheer_file_lines)==0):
        return -1
    cheer_amount = int(cheer_file_lines[0])
    return cheer_amount

# ADD TWITCH FOLLOW LOGS
def add_twitch_follow_logs(previous_follow_amount: int) -> int:
    new_follow_amount = get_twitch_follow_amount()
    for i in range(new_follow_amount - previous_follow_amount):
        supabase.table("logs").insert({"type":"TWITCH_FOLLOW"}).execute()
    return new_follow_amount

# ADD TWITCH SUB LOGS
def add_twitch_sub_logs(previous_sub_amount: int) -> int:
    new_sub_amount = get_twitch_sub_amount()
    for i in range(new_sub_amount - previous_sub_amount):
        supabase.table("logs").insert({"type":"TWITCH_SUB"}).execute()
    return new_sub_amount

# ADD TWITCH CHEER LOGS
def add_twitch_cheer_logs(previous_cheer_amount: int) -> int:
    new_cheer_amount = get_twitch_cheer_amount()
    delta_cheer_amount = new_cheer_amount - previous_cheer_amount
    if delta_cheer_amount > 0:
        supabase.table("logs").insert({"type":"TWITCH_CHEER", "number":delta_cheer_amount}).execute()
    return new_cheer_amount

# ADD TWITCH VIEWS LOGS
def add_twitch_views_logs() -> None:
    oauth_request_payload: dict = {'client_id': twitch_api_client_id, 'client_secret': twitch_api_client_secret, 'grant_type': 'client_credentials'}
    oauth_token: str = requests.post(url = twitch_api_oauth_request_url, data = oauth_request_payload).json()["access_token"]

    stream_request_params: dict = {'user_login':'TWITCH USERNAME'}, #REPLACE BY YOUR TWITCH USERNAME
    stream_request_headers: dict = {'Client-Id':twitch_api_client_id, 'Authorization':'Bearer '+oauth_token}
    stream_response = requests.get(url = twitch_api_streams_request_url, params = stream_request_params, headers = stream_request_headers)

    if(stream_response.json()["data"]):
        views_number: str = stream_response.json()["data"][0]["viewer_count"]
        supabase.table("logs").insert({"type":"TWITCH_VIEW", "number":views_number}).execute()


# SEP-LOG
def sep_log() -> None:
    current_follow_amount: int = get_twitch_follow_amount()
    current_sub_amount: int = get_twitch_sub_amount()
    current_cheer_amount: int = get_twitch_cheer_amount()
    previous_view_update: int = datetime.now().minute
    while(not thread_killer):
        add_point_stages_logs()
        add_patreon_logs()
        current_follow_amount = add_twitch_follow_logs(current_follow_amount)
        current_sub_amount = add_twitch_sub_logs(current_sub_amount)
        current_cheer_amount = add_twitch_cheer_logs(current_cheer_amount)
        if datetime.now().minute != previous_view_update:
            add_twitch_views_logs()
            previous_view_update = datetime.now().minute

        time.sleep(sleep_time)


# MAIN
def main():
    global thread_killer
    
    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____        _                 \n  / ____|  ____|  __ \      | |                \n | (___ | |__  | |__) |_____| |     ___   __ _ \n  \___ \|  __| |  ___/______| |    / _ \ / _` |\n  ____) | |____| |          | |___| (_) | (_| |\n |_____/|______|_|          |______\___/ \__, |\n                                          __/ |\n                                         |___/ " + END)
    print("\nSEP-Log : StreamEventPoint Log python script\nby V. / @Vinus - (version 1.0.0)")
    print("\nTo quit, keep pressing \"suppr\"\n")

    sep_log_thread = Thread(target=sep_log)
    sep_log_thread.start()

    while(True):
        if(keyboard.is_pressed('suppr')):
            thread_killer = False#True
            break

    sep_log_thread.join()

    print("END.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()