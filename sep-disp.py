# -*- coding: utf-8 -*-
"""
   _____ ______ _____        _____  _           
  / ____|  ____|  __ \      |  __ \(_)          
 | (___ | |__  | |__) |_____| |  | |_ ___ _ __  
  \___ \|  __| |  ___/______| |  | | / __| '_ \ 
  ____) | |____| |          | |__| | \__ \ |_) |
 |_____/|______|_|          |_____/|_|___/ .__/ 
                                         | |    
                                         |_|    
                                                
SEP-Disp : StreamEventPoint Display python script
- Get point informations
- Display point total amount
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
from tkinter import *


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

# THREAD TOOLS
thread_killer: bool = False
sleep_time: int = config_json['connection']['request_interval']

# OUTPUTS
output_filename: str = config_json['display_output']['file']['folder'] + '\\' + config_json['display_output']['file']['filename']

# VISUAL INTERFACE
point_label = Label()
window_width: int = config_json['display_output']['screen']['window_width']
window_height: int = config_json['display_output']['screen']['window_height']
font_size: int = config_json['display_output']['screen']['font_size']
interface_sleep_time: int = config_json['display_output']['screen']['update_interval'] * 1000


# PRINT TOTAL POINTS AMOUNT IN FILE
def file_writer() -> None:
    previous_rank: int = 0
    while(not thread_killer):
        point_total = supabase.table("point-total").select("rank, point_total").gte("rank",previous_rank).order("rank", desc=False).execute().data[-1]
        total_points_amount: int = point_total["point_total"]
        previous_rank = point_total["rank"]

        with open(output_filename, 'w') as point_file:
            point_file.write(str(total_points_amount))

        time.sleep(sleep_time)


# INTERFACE
def interface_updater() -> None:
    global point_label

    total_points_amount: int = supabase.table("point-total").select("rank, point_total").order("rank", desc=False).execute().data[-1]["point_total"]
    point_label.config(text=str(total_points_amount))

    point_label.after(interface_sleep_time, interface_updater)

def interface_creator() -> None:
    global point_label

    window = Tk()
    window.minsize(window_width, window_height)
    window.title("SEP-Disp : StreamEventPoint Display")
    window.configure(bg="#1d272a")
    window.iconbitmap(default=os.getcwd()+'/src/point.ico')

    point_label = Label(window, text=str("[init...]"), font=("Roboto", font_size), fg="#dfa549", bg="#1d272a")
    point_label.pack()

    interface_updater()

    window.mainloop()


# MAIN
def main():
    global thread_killer

    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____        _____  _           \n  / ____|  ____|  __ \      |  __ \(_)          \n | (___ | |__  | |__) |_____| |  | |_ ___ _ __  \n  \___ \|  __| |  ___/______| |  | | / __| '_ \ \n  ____) | |____| |          | |__| | \__ \ |_) |\n |_____/|______|_|          |_____/|_|___/ .__/ \n                                         | |    \n                                         |_|    " + END)
    print("\nSEP-Disp : StreamEventPoint Display python script\nby V. / @Vinus - (version 1.0.0)")
    print("\nTo quit, keep pressing \"suppr\"\n")

    file_writer_thread = Thread(target=file_writer)
    file_writer_thread.start()

    interface_thread = Thread(target=interface_creator)
    interface_thread.start()

    while(True):
        if(keyboard.is_pressed('suppr')):
            thread_killer = True
            break

    file_writer_thread.join()
    interface_thread.join()

    print("END.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()