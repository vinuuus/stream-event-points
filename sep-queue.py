# -*- coding: utf-8 -*-
"""
   _____ ______ _____         ____                        
  / ____|  ____|  __ \       / __ \                       
 | (___ | |__  | |__) |_____| |  | |_   _  ___ _   _  ___ 
  \___ \|  __| |  ___/______| |  | | | | |/ _ \ | | |/ _ \
  ____) | |____| |          | |__| | |_| |  __/ |_| |  __/
 |_____/|______|_|           \___\_\\__,_|\___|\__,_|\___|
                                                          
SEP-Queue : StreamEventPoint Queue python script
- Get case informations
- Print queue
@version: 1.0.0
@author: V. / @Vinus
"""


# IMPORTS
from supabase import create_client
import warnings
from functools import partial
import os
import json
from tkinter import *
from tkinter.messagebox import *


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

# SOURCE FOLDER
main_folder: str = os.getcwd() + '/'

# VISUAL INTERFACE
window = None
buttons_grid: list = []
case_id_grid: list = []
background_color: str = '#1d272a'
button_colors: dict = {'JAUNE':'#f2d51f', 'MAUVE':'#ac6ac7', 'BLEU':'#45a9ec', 'ROUGE':'#f85d4d', 'VERT':'#3fdd82', 'GRIS':'#ced4d8', 'NOIR':'#ffffff'}
interface_sleep_time: int = config_json['display_output']['screen']['update_interval'] * 1000
total_rows_number: int = 15
case_height: int = 1
case_width: int = 100
interface_height: int = 50*total_rows_number*case_height
interface_width: int = 800


# CLICKED BUTTON FUNCTION
def button_clicked(row: int) -> None:
    global buttons_grid
    global case_id_grid
    if case_id_grid[row] != 0:
        buttons_grid[row].configure(text="",
                                    bg=background_color,
                                    activebackground=background_color)
        supabase.table("grid").update({"done":True}).eq("id",case_id_grid[row]).execute()
        case_id_grid[row] = 0

# QUEUE UPDATER
def interface_updater() -> None:
    global window
    global buttons_grid
    global case_id_grid 

    todo_cases: list = supabase.table("grid").select("id, type, infos, color, winner, opened, done").eq("opened",True).eq("done",False).execute().data

    todo_cases_index = 0
    while 0 in case_id_grid and todo_cases_index < len(todo_cases):
        case: dict = todo_cases[todo_cases_index]
        if case["id"] not in case_id_grid:
            row: int = case_id_grid.index(0)
            if(case["infos"]!=""):
                buttons_grid[row].configure(text="["+str(case["id"])+"] "+case["type"]+" ("+case["infos"]+") - "+case["winner"],
                                        bg=button_colors[case["color"]],
                                        activebackground=button_colors[case["color"]])
            else: 
                buttons_grid[row].configure(text="["+str(case["id"])+"] "+case["type"]+" - "+case["winner"],
                                        bg=button_colors[case["color"]],
                                        activebackground=button_colors[case["color"]])
            case_id_grid[row] = case["id"]
        todo_cases_index += 1

    window.after(interface_sleep_time, interface_updater)


# MAIN
def main():
    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____         ____                        \n  / ____|  ____|  __ \       / __ \                       \n | (___ | |__  | |__) |_____| |  | |_   _  ___ _   _  ___ \n  \___ \|  __| |  ___/______| |  | | | | |/ _ \ | | |/ _ \\\n  ____) | |____| |          | |__| | |_| |  __/ |_| |  __/\n |_____/|______|_|           \___\_\\\\__,_|\___|\__,_|\___|" + END)
    print("\nSEP-Queue : StreamEventPoint Queue python script\nby V. / @Vinus - (version 1.0.0)\n")

    global window
    global buttons_grid
    global case_id_grid 
    global main_folder

    warnings.simplefilter('ignore')

    #window creation
    window = Tk()
    window.title("SEP-Queue : StreamEventPoint Queue")
    window.resizable(False, False)
    window.geometry(str(interface_width)+"x"+str(interface_height))
    window.configure(bg=background_color)
    window.iconbitmap(default = main_folder + 'src/point.ico')

    #button grid
    main_grid_frame = Frame(window)
    main_grid_frame.config(bg = background_color)
    for row in range(total_rows_number):
        case_id_grid.append(0)
        buttons_grid.append(Button(main_grid_frame,
                                   relief=SUNKEN,
                                   text="",
                                   justify=LEFT,
                                   anchor="w",
                                   bd=0,
                                   bg=background_color,
                                   activebackground=background_color,
                                   fg="#000000",
                                   activeforeground="#000000",
                                   font=("Calibri", 15, "bold italic"),
                                   width=case_width,
                                   height=case_height,
                                   command=partial(button_clicked, row)))
        buttons_grid[row].grid(row=row, column=0, padx = 5, pady = 5)

    #pack all
    main_grid_frame.pack(side="top", padx = 5, pady = 5, expand=True, fill="both")

    interface_updater()

    window.mainloop()

    print("END.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()