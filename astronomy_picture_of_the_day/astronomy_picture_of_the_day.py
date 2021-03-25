#!/usr/bin/python

# Importing custom files
import sys
sys.path.insert(1, '../')

import utils
import instagram

from datetime import date
from bs4 import BeautifulSoup
import requests
import wget
import json
import os

def main(debug):

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Getting parameters
    params_file = 'params.json'
    params = utils.get_params(params_file)

    username = params['username']
    password = params['password']
    previous_post_key = params['previous_post_key']

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Defining edited parameters dictionary
    edit_params = {}

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Custom part of the bot

    base_url = 'https://apod.nasa.gov/apod/'
    today = date.today()
    today_url = 'ap' + today.strftime("%y%m%d") + '.html'
    url = base_url + today_url

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    # If the page for the current date does not exist, there is nothing to post
    if str(page) == '<Response [404]>':
        print("\n\n\nThere is nothing new to post\n\nDONE")
        exit(0)

    img_name = soup.findAll(name='b')[0].text.strip()
    
    # We do the check on the image name
    if previous_post_key != "" and previous_post_key == img_name:
        print("\n\n\nThere is nothing new to post\n\nDONE")
        exit(0)

    img_credit = soup.findAll(name='a')[3].text.strip()

    # Setting the previous post key
    edit_params['previous_post_key'] = img_name

    par_tag = soup.findAll(name='p')
    caption = par_tag[2]

    # The caption paragraph contains another p
    # that needs to be removed
    for p in caption.findAll(name='p'):
        p.extract() 

    if(len(caption.findAll(name='b')) > 0):
        caption.findAll(name='b')[0].extract() 

    hashtags = '#stars #nasa #astronomy #apod #dailyposting'
    caption = img_name + ' (by ' + img_credit + ')' + '\n\n' + caption.text.replace('\n', ' ').replace('  ', ' ').strip() + '\n\n' + today.strftime("%B %d, %Y") +  '\n\n' + hashtags

    print('Caption:\n\n')
    print(caption)
    print()

    img_tag = soup.findAll(name='img')[0]
    img_src = img_tag['src']
    image_link = base_url + img_src
    image_ext = image_link[-4:]
    image_file = 'img' + image_ext

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    print("Downloading image")
    utils.download_image(image_file, image_link)

    # Getting average color in image and saving as background
    print("Setting bakground color")
    utils.img_bg_color(image_file, 'bg.jpg')

    print("\n\nCompliling tex file")
    if debug:
        utils.compile_latex_verbose()
    else:
        utils.compile_latex_silent()

    print("\n\nTransforming pdf in jpg")
    utils.pdf_2_jpg('latex/main.pdf', 'out.jpg')

    if not debug:

        print("Posting to instagram")
        instagram.post_image('out.jpg', full_caption, username, password)
    
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
