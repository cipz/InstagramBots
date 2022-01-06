#!/usr/bin/python

# Importing custom files
import sys
sys.path.insert(1, '../')

import utils
import instagram

from datetime import date
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup
import urllib.request
import requests
import time
import wget
import json
import os

def main(debug):
    
    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Getting parameters
    params_file = 'params.json'
    params = utils.get_params(params_file, 'santo_username', 'santo_password')

    username = params['username']
    password = params['password']
    previous_post_key = params['previous_post_key']

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Defining edited parameters dictionary
    edit_params = {}

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Custom part of the bot

    base_url = 'https://www.santodelgiorno.it'

    # Getting article itself
    print("Downloading article")
    today_article_page = requests.get(base_url)
    today_article_soup = BeautifulSoup(today_article_page.content, 'html.parser')

    giorno = today_article_soup.find('span', {'class':'Titolo'}).text

    # We do the check on the article URL
    if previous_post_key == giorno:
        print("\n\n\nThere is nothing new to post\n\nDONE")
        exit(0)

    # Setting the previous post key
    edit_params['previous_post_key'] = giorno

    today_main_div = today_article_soup.find('div', {'id':'CenterDiv'})
    santo_url = today_main_div.find('a')['href']

    url = base_url + santo_url

    print("CURRENT URL:" , url)

    santo_main_page = requests.get(url)
    santo_main_page_soup =  BeautifulSoup(santo_main_page.content, 'html.parser')

    santo_main_div = santo_main_page_soup.find('div', {'id':'CenterDiv'})

    nome_santo = santo_main_div.find('h1').text
    foto_santo_url = santo_main_div.find('img')['data-src']
    descrizione_santo = santo_main_div.find('div',{'style':'float: left;text-align: justify;width: 492px;margin-left: 30px;font-size: 16px;padding: 10px;background-color: #f7f0e830;'})

    for div in descrizione_santo.findAll('div'):
        div.decompose()

    for br in descrizione_santo.findAll('br'):
        br.replace_with('\n')

    descrizione_santo = descrizione_santo.text.strip()

    descrizione_santo_taglio = descrizione_santo.split('PRATICA')
    caption = descrizione_santo_taglio[0]
    caption_max_len = 1600
    new_caption = ''

    if len(caption) > caption_max_len:

        frasi = caption.split('.')

        new_caption = ''

        frasi_count = 0
        while len(new_caption) < caption_max_len:
            new_caption = new_caption + frasi[frasi_count].strip() + '. '
            frasi_count += 1

        # new_caption = new_caption + '.'

        coda = '\n\nPer la descrizione completa continuare su \'santodelgiorno.it\''
        new_caption = new_caption.strip() + coda

    if len(new_caption) > 0:
        caption = new_caption

    hashtags = '#santo #chiesa #cristo #cristianesimo'
    hashtags += '\n'
    for word in nome_santo.split():
        hashtags += '#' + word  + " "

    today = date.today()
    anno = today.strftime("%Y")

    giorno_caption = giorno.replace('Oggi','').replace('si venera:','').strip() + ' ' + anno
    full_caption = nome_santo + '\n\n' + caption + '\n\n' + giorno_caption + '\n\n' + hashtags

    print("CAPTION:" , full_caption)

    # Setting image information    
    image_link = base_url + foto_santo_url
    image_ext = image_link[-4:]
    image_file = 'img' + image_ext

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    print("Downloading image")
    utils.download_image(image_file, image_link)
    
    # Getting average color in image and saving as background
    print("Setting bakground color")
    utils.img_bg_color('img.jpg', 'bg.jpg')
    
    print("\n\nCompliling tex file")
    # utils.compile_latex_verbose()
    utils.compile_latex_silent()
    
    print("\n\nTransforming pdf in jpg")
    utils.pdf_2_jpg('latex/main.pdf', 'out.jpg')

    if not debug:

        execution_result = {}
        execution_result["color"] =  "green"

        try:

            print("Posting to instagram")
            instagram.post_image('out.jpg', full_caption, username, password)
            print('Setting new parameters')
            utils.set_params(params_file, edit_params)

        except Exception as e:

            execution_result["color"] =  "red"

        utils.edit_badge("ilsantodioggi.json", execution_result)

        # Removing stuff (not necessary if used in docker container of github actions)
        # Useful if executed locally
        print("Removing useless files")
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
