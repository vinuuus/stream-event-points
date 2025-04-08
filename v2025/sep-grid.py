# -*- coding: utf-8 -*-
"""
   _____ ______ _____         _____      _     _ 
  / ____|  ____|  __ \       / ____|    (_)   | |
 | (___ | |__  | |__) |_____| |  __ _ __ _  __| |
  \___ \|  __| |  ___/______| | |_ | '__| |/ _` |
  ____) | |____| |          | |__| | |  | | (_| |
 |_____/|______|_|           \_____|_|  |_|\__,_|
                                                 
SEP-Grid : StreamEventPoint Grid python script
- Get case informations
- Print grid
@version: 1.0.0
@author: V. / @Vinus
"""


# IMPORTS
from supabase import create_client
import os
import json
import warnings
import math
from tkinter import *
from tkinter.messagebox import *
from PIL import Image, ImageTk


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
buttons_images: list = []
buttons_revealed_images: list = []
background_color: str = '#ff5ccd'
interface_sleep_time: int = config_json['display_output']['screen']['update_interval'] * 1000
total_rows_number: int = 9
total_cols_number: int = 16
case_size: int = 86
interface_height: int = 900
interface_width: int = math.ceil(interface_height*1.94)


# GRID UPDATER
def interface_updater():
    global window
    global buttons_grid
    global buttons_revealed_images

    opened_cases: list = supabase.table("grid").select("id, type, opened").eq("opened",True).eq("displayed",False).execute().data

    for case in opened_cases:
        case_id: int = case["id"]
        case_col: int = case_id%total_cols_number-1
        if case_col == -1:
            case_row: int = case_id//total_cols_number-1
        else:
            case_row: int = case_id//total_cols_number

        buttons_grid[case_row][case_col].configure(image = buttons_revealed_images[case_row][case_col])
        supabase.table("grid").update({"displayed":True}).eq("id",case["id"]).execute()

    window.after(interface_sleep_time, interface_updater)


# MAIN
def main():
    print(BOLD + BRIGHT_YELLOW + "\n\n   _____ ______ _____         _____      _     _ \n  / ____|  ____|  __ \       / ____|    (_)   | |\n | (___ | |__  | |__) |_____| |  __ _ __ _  __| |\n  \___ \|  __| |  ___/______| | |_ | '__| |/ _` |\n  ____) | |____| |          | |__| | |  | | (_| |\n |_____/|______|_|           \_____|_|  |_|\__,_|" + END)
    print("\nSEP-Grid : StreamEventPoint Grid python script\nby V. / @Vinus - (version 1.0.0)\n")

    global window
    global buttons_grid
    global buttons_images
    global buttons_revealed_images
    global main_folder

    warnings.simplefilter('ignore')

    #window creation
    window = Tk()
    window.title("SEP-Grid : StreamEventPoint Grid")
    window.resizable(False, False)
    window.geometry(str(interface_width)+"x"+str(interface_height))
    window.configure(bg=background_color)
    window.iconbitmap(default = main_folder + 'src/point.ico')

    #button grid
    main_grid_frame = Frame(window)
    main_grid_frame.config(bg = background_color)
    id: int = 0
    for row in range(total_rows_number):
        buttons_grid.append([])
        buttons_images.append([])
        buttons_revealed_images.append([])
        for col in range(total_cols_number):
            id+=1

            grid_case_image = ImageTk.PhotoImage(Image.open(main_folder+'src/case_'+str(id)+'.png').resize((case_size,case_size)))
            buttons_images[row].append(grid_case_image)

            case_type: str = supabase.table("grid").select("id, type").eq("id",id).execute().data[0]["type"]
            grid_case_revealed_image = ImageTk.PhotoImage(Image.open(main_folder+'src/case_revealed_'+case_type+'.png').resize((case_size,case_size)))
            buttons_revealed_images[row].append(grid_case_revealed_image)
            
            buttons_grid[row].append(Button(main_grid_frame, relief=SUNKEN, image=grid_case_image, bd=0, bg=background_color, activebackground=background_color, width=case_size, height=case_size))
            buttons_grid[row][col].grid(row=row, column=col, padx = 5, pady = 5)

    #final case
    final_case_frame = Frame(window)
    final_case_frame.config(bg = background_color)
    final_case_image = ImageTk.PhotoImage(Image.open(main_folder+'src/case_locked.png').resize((case_size,case_size)))
    final_case = Button(final_case_frame, relief=SUNKEN, image=final_case_image, bd=0, bg=background_color, activebackground=background_color, width=case_size, height=case_size)
    final_case.pack(padx = 5)

    #pack all
    main_grid_frame.pack(side="left", padx = 5, pady = 5)
    final_case_frame.pack(side="right", padx = 35)

    interface_updater()

    window.mainloop()

    print("END.\nThe program has been killed normally.\n\n")

if __name__ == "__main__":
    main()