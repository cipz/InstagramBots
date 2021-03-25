#!/usr/bin/python

# Importing custom files
import sys
sys.path.insert(1, '../')

import utils
import instagram

from datetime import date
from PIL import Image, ImageDraw
import time
import json
import os

def main(debug):
    
    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Getting parameters
    params_file = 'params.json'
    params = utils.get_params(params_file, 'colors_username', 'colors_password')

    username = params['username']
    password = params['password']
    previous_post_key = params['previous_post_key']

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Defining edited parameters dictionary
    edit_params = {}

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Custom part of the bot

    previous_post_color_index = previous_post_key
    new_color_index = int(previous_post_color_index) + 1

    # Get colors from file
    colors_json_file = 'colors_sorted.json'
    colors = {}
    with open(colors_json_file, 'r') as myfile:
        data = myfile.read()
    
    colors = json.loads(data)
    colors_list = list(colors)
    total_colors = len(colors_list)

    if new_color_index >= total_colors:
        print("\n\n\nThere are no more colors to post\n\nDONE")
        exit(0)

    new_color = colors[colors_list[new_color_index]]

    # Setting the previous post key
    edit_params['previous_post_key'] = str(new_color_index)

    new_color_hex = new_color["hex"][1:]
    if len(new_color_hex) < 6:
        new_color_hex = '0'*(6-len(new_color_hex)) + new_color_hex

    # Setting latex colors
    print("\n\nSetting correct values in tex file")
    colors_file = open('latex/colors.txt', 'r+')
    colors_file.truncate(0)

    line = "\\definecolor{bck_color}{HTML}{" + new_color_hex + "}"
    colors_file.write(line + "\n")

    line = "\\definecolor{complementary_color}{HTML}{" + new_color["complementary"][1:] + "}"
    colors_file.write(line + "\n")

    color_name = new_color["name"]
    color_name = color_name.replace("#", "\\#")
    color_name = color_name.replace("&", "\\&")
    
    splits = []
    if len(color_name) > 15:
        splits = color_name.split(" ")

        color_name = "{\\Large "
        tmp_len = 0
        for split in splits:
            tmp_len += len(split)
            color_name = color_name + " " + split
        
            if tmp_len > 9:
                tmp_len = 0
                color_name = color_name + "\\\\"


        color_name = color_name + "}"
    elif len(color_name) > 10:
        color_name = "{\Large " + color_name + "}"

    line = "\\newcommand{\\maincolor}{" + color_name + "}"
    colors_file.write(line + "\n")

    line = "\\newcommand{\\hexvalue}{\\#" + new_color_hex + "}"
    colors_file.write(line + "\n")

    colors_file.close()

    caption = ""

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 
    
    print("\n\nCompliling tex file")
    if debug:
        utils.compile_xelatex_verbose()
    else:
        utils.compile_xelatex_silent()
    
    print("\n\nTransforming pdf in jpg")
    utils.pdf_2_jpg('latex/main.pdf', 'out.jpg')

    if not debug:

        print("Posting to instagram")
        instagram.post_image('out.jpg', caption, username, password)
    
        print('Setting new parameters')
        utils.set_params(params_file, edit_params)

        # Removing stuff (not necessary if used in docker container of github actions)
        # In case of local it could be userful
        print("Removing unused files")
        os.system('rm "' + image_file + '"')
        os.system('rm *REMOVE_ME')
        os.system('rm img.jpg')
        os.system('rm out.jpg')   

if __name__ == "__main__":

    if "--debug" in sys.argv[1:]:
        debug=True
    elif "-d" in sys.argv[1:]:
        debug=True
    else:
        debug=False

    main(debug)

    print("\nDONE")
