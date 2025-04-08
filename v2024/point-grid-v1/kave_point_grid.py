# -*- coding: utf-8 -*-
"""
  _____      _       _                    _     _ 
 |  __ \    (_)     | |                  (_)   | |
 | |__) |__  _ _ __ | |_ ______ __ _ _ __ _  __| |
 |  ___/ _ \| | '_ \| __|______/ _` | '__| |/ _` |
 | |  | (_) | | | | | |_      | (_| | |  | | (_| |
 |_|   \___/|_|_| |_|\__|      \__, |_|  |_|\__,_|
                                __/ |             
                               |___/              
Kave Point-Grid : Python script for point grid
@version: 1.0.0
@author: V. / @Vinus
"""

#LIBRAIRIES
from functools import partial
import webbrowser
from math import *
import warnings
import os

from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
from PIL import Image, ImageTk

import gspread
from oauth2client.service_account import ServiceAccountCredentials


#PRINT CONSTANTS
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


#GLOBAL VARS
main_folder = os.getcwd() + '/'


#GLOBAL API VARS
scope = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.file']
SHEET_ID = 'A'
SHEET_NOM = 'B'
SHEET_COLOR = 'E'
SHEET_REVEALED = 'F'


#GLOBAL UI VARS
window = None
buttons_grid = []
buttons_grid_ids = []
buttons_images = []
buttons_revealed_images = []
background_color = '#ff5ccd'



#UI FUNCTIONS
def case_clicked(row, col):
    global buttons_grid_ids
    global buttons_grid
    global buttons_revealed_images
    global scope

    button_number = buttons_grid_ids[row][col]

    creds = ServiceAccountCredentials.from_json_keyfile_name(main_folder + 'src/client_key.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('3_ANS-DOCUMENT_SUIVI').get_worksheet(2)
    sheet_row = sheet.row_values(button_number+2)

    print(RED+BOLD+str(button_number)+END+' - REF='+'['+str(row)+','+str(col)+'] '+"LINE="+DARK_GRAY+ITALIC+str(sheet_row)+END)

    grid_case_revealed_image = ImageTk.PhotoImage(Image.open(main_folder+'src/case_revealed_'+sheet_row[1]+'.png').resize((86,86)))
    buttons_revealed_images[row][col] = grid_case_revealed_image

    sheet.update(values = [[True]], range_name = SHEET_REVEALED + str(button_number+2))
    buttons_grid[row][col].configure(image = buttons_revealed_images[row][col])


#MAIN
def main():
    global window
    global buttons_grid
    global buttons_grid_ids
    global buttons_images
    global buttons_revealed_images
    global main_folder

    warnings.simplefilter('ignore')

    height = 900
    width = ceil(height*1.94)

    #window creation
    window = Tk()
    window.title("Kave Point Grid v.1")
    window.resizable(False, False)
    window.geometry(str(width)+"x"+str(height))
    window.configure(bg=background_color)
    window.iconbitmap(default = main_folder + 'src/point.ico')

    #button grid
    main_grid_frame = Frame(window)
    main_grid_frame.config(bg = background_color)
    id=0
    for row in range(9):
        buttons_grid.append([])
        buttons_grid_ids.append([])
        buttons_images.append([])
        buttons_revealed_images.append([])
        for col in range(16):
            id+=1
            buttons_grid_ids[row].append(id)

            grid_case_image = ImageTk.PhotoImage(Image.open(main_folder+'src/case_'+str(id)+'.png').resize((86,86)))
            buttons_images[row].append(grid_case_image)

            grid_case_revealed_image = ImageTk.PhotoImage(Image.open(main_folder+'src/case.png').resize((86,86)))
            buttons_revealed_images[row].append(grid_case_revealed_image)
            
            buttons_grid[row].append(Button(main_grid_frame, relief=SUNKEN, image=grid_case_image, bd=0, bg=background_color, activebackground=background_color, width=86, height=86, command=partial(case_clicked, row, col))) #buttons_grid[row].append(Button(main_grid_frame, text=id, bd=0, bg="#f3dab2", relief=SUNKEN, activebackground="#f3dab2", width=5, height=5, command=partial(case_clicked, row, col)))
            buttons_grid[row][col].grid(row=row, column=col, padx = 5, pady = 5)

    #final case
    final_case_frame = Frame(window)
    final_case_frame.config(bg = background_color)
    final_case_image = ImageTk.PhotoImage(Image.open(main_folder+'src/case_locked.png').resize((86,86)))
    final_case = Button(final_case_frame, relief=SUNKEN, image=final_case_image, bd=0, bg=background_color, activebackground=background_color, width=86, height=86, command=window.destroy)
    final_case.pack(padx = 5)

    #pack ALL
    main_grid_frame.pack(side="left", padx = 5, pady = 5)
    final_case_frame.pack(side="right", padx = 35)

    window.mainloop()
    
#execute main ssi le script a ete appele directement
#(ne s execute pas si integre dans un autre fichier)
if __name__ == "__main__":
    main()
