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
    params = utils.get_params(params_file, 'zanichelli_username', 'zanichelli_password')

    username = params['username']
    password = params['password']
    previous_post_key = params['previous_post_key']

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Defining edited parameters dictionary
    edit_params = {}

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    print("Setting url and downloading content")
    url = 'https://dizionaripiu.zanichelli.it/cultura-e-attualita/le-parole-del-giorno/parola-del-giorno/'

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    parola_title = soup.find('header', {'class':'mb-4'}).text.strip()

    # Checking word
    if previous_post_key != "" and previous_post_key == parola_title:
        print("\n\n\nThere is nothing new to post\n\nDONE")
        exit(0)

    # Setting the previous post key
    edit_params['previous_post_key'] = parola_title


    main_div = soup.find('div', {'class': 'main-content light-txt'})
    
    sillabazione = main_div.find('span', {'style': 'display: inline; font-style: normal; font-weight: 300; font-size: 1em; color: #C53329; font-family: "Noto Sans", Verdana, Georgia, Tahoma, sans-serif !important;'}).text.strip()

    tipologia_parola = main_div.find('span', {'style':'display: inline; font-style: normal; font-weight: 600; font-size: 1em; color: #444; font-family: "Noto Sans", Verdana, Georgia, Tahoma, sans-serif !important;'}).text.strip()

    info_parola = main_div.findAll('span', {'style':'display: inline; font-style: normal; font-weight: 300; font-size: 1em; color: #444; font-family: "Noto Sans", Verdana, Georgia, Tahoma, sans-serif !important;'})
    
    pronuncia_parola = info_parola[0].text
    origine_parola = info_parola[1].text

    significati_parola = main_div.findAll('div', {'style': 'display: block; background-color: #FFFFFF; margin-top: 1em; margin-left: 0em; padding-bottom: 0.9em; border-bottom-style: solid; border-bottom-color: #ccc; border-bottom-width: 1px;'})

    caption_significati = ''

    if len(significati_parola) > 1:
        for significato in significati_parola:

            if len(caption_significati) > 1600:
                break

            significato_entry = significato.find('p')
            significato_entry_text = significato_entry.text.strip()
            significato_entry_text = ' '.join(significato_entry_text.split())

            caption_significati += '\n' + significato_entry_text
    else:
        caption_significati += '\n' + significati_parola[0].text

    data = soup.find('div', {'class':'article-meta col text-right'}).text

    # Setting caption
    print("Setting caption")
    hashtags = '#' + parola_title + ' #zanichelli #dizionario #paroladelgiorno #grammatica #cultura #italia #linguaitaliana'
    caption = 'La parola del giorno è: ' + parola_title + '\n' + caption_significati + '\n\n' + data + '\n\n' + hashtags

    print("Caption:\n\n")
    print(caption)
    print()

    print("\n\nSetting correct values in tex file")
    words_file = open('latex/words.txt', 'r+')
    words_file.truncate(0)

    # A long word just to test
    # parola_title = 'Supercalifragilistichespiralidoso'

    # If the word is too long and does not fit the picture
    len_parola_title = len(parola_title)
    # print(len_parola_title)
    if len_parola_title > 30:
        parola_title = '\\footnotesize ' + parola_title

    elif len_parola_title > 19:
        parola_title = '\small ' + parola_title

    elif len_parola_title > 10:

        if ' / ' in parola_title:
            parola_title = parola_title.replace(' / ', ' / \\newline ')
        elif ' ' in parola_title:
            parola_title = parola_title.replace(' ', '\\newline ')
        else:
            parola_title = '\LARGE ' + parola_title

    line = '\\newcommand{\parolatitle}{' + parola_title + '}'
    words_file.write(line)

    line = '\\newcommand{\sillabazione}{' + sillabazione + '}'
    words_file.write(line)

    if len(origine_parola) > 60:
        tipologia_parolas = '{\\scriptsize' + tipologia_parola + '}'
        origine_parola = '{\\begin{spacing}{0.85}\\noindent\\footnotesize' + origine_parola + '\end{spacing}}'

    line = '\\newcommand{\\tipologiaparola}{' + tipologia_parola + '}'
    words_file.write(line)

    line = '\\newcommand{\origineparola}{' + origine_parola + '}'
    words_file.write(line)

    line = '\\newcommand{\data}{' + data + '}'
    words_file.write(line)

    words_file.close()

    print("\n\nCompliling tex file")
    # utils.compile_xelatex_verbose()
    utils.compile_xelatex_silent()
    
    print("\n\nTransforming pdf in jpg")
    utils.pdf_2_jpg('latex/main.pdf', 'out.jpg')

    if not debug:

        print("Posting to instagram")
        instagram.post_image('out.jpg', full_caption, username, password)

        print('Setting new parameters')
        utils.set_params(params_file, edit_params)
    
        # Removing stuff (not necessary if used in docker container of github actions)
        # Useful if executed locally
        print("Removing useless files")
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