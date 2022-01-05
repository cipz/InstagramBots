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
    params = utils.get_params(params_file, 'wikipedia_picture_username', 'wikipedia_picture_password')

    username = params['username']
    password = params['password']
    previous_post_key = params['previous_post_key']

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Defining edited parameters dictionary
    edit_params = {}

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    base_url = 'https://en.wikipedia.org/wiki/Template:POTD/'
    
    # It does not work otherwise, must look into it
    from datetime import date
    today = date.today()

    date = today.strftime("%Y-%m-%d")
    date_url = date.replace(' ', '_')

    # We do the check on the article URL
    if previous_post_key == date_url:
        print("\n\n\nThere is nothing new to post\n\nDONE")
        exit(0)

    # Setting the previous post key
    edit_params['previous_post_key'] = date_url

    url = base_url + date

    # Getting article itself
    print("Downloading article")
    today_article_page = requests.get(url)
    today_article_soup = BeautifulSoup(today_article_page.content, 'html.parser')

    # Getting article description
    article_description_main_div = today_article_soup.find('div',{'style':'box-sizing: border-box; margin:0.5em; width: 600px; border: 3px #ccccff solid; padding: 11px; text-align: center; background-color: white;'})
    full_article_description = article_description_main_div.text.replace('Archive – More featured pictures... ', '').replace('Picture of the day','').strip()

    article_description = ''
    photo_credit = ''

    if 'Photograph credit:' in full_article_description:
        article_description = full_article_description.split('Photograph credit:')[0].strip()
        photo_credit = '\n\nCredit: ' + full_article_description.split('Photograph credit:')[1].split('Archive')[0].strip()
    elif 'Engraving credit:' in full_article_description:
        article_description = full_article_description.split(('Engraving credit:'))[0].strip()
        photo_credit = '\n\nCredit: ' + full_article_description.split('Engraving credit:')[1].split('Archive')[0].strip()

    reject_text = 'Wikipedia does not have a project page with this exact name.'
    if reject_text in article_description:
        print("There is nothing new to post")
        exit()

    # print(article_description)
    # print(photo_credit)

    image_link = 'https:' + today_article_soup.find('a',{'class':'image'}).find('img')['srcset'].split(' ')[-2:-1][0]

    # print(image_link)

    image_ext = image_link[-4:]
    image_file = 'img' + image_ext

    print("Downloading image")
    f = open(image_file,'wb')
    f.write(urllib.request.urlopen(image_link).read())
    f.close()
    print("Image downloaded")

    print("\n\nCompliling tex file")
    # Twice because the first time it may not get the images' position correctly
    os.system("cd latex ; pdflatex main.tex >> /dev/null ; pdflatex main.tex >> /dev/null")
    # pdflatex is very verbose and useful to test if / where an error occors
    # os.system("cd latex ; pdflatex main.tex ; pdflatex main.tex")

    print("\n\nTransforming pdf in jpg")
    utils.pdf_2_jpg('latex/main.pdf', 'out.jpg')

    # Getting a better date
    date = today.strftime("%B %d, %Y")

    print(date)

    # Setting caption
    print('Setting full caption with date and hashtags')
    hashtags = '#wikipedia #articleoftheday #bestoftheday'
    full_caption = article_description + '\n\n' + date + photo_credit + '\n\n' + hashtags

    print("Full caption:\n")
    print(full_caption)
    print()

    if not debug:

        print("Posting to instagram")
        instagram.post_image('out.jpg', full_caption, username, password)

        print('Setting new parameters')
        utils.set_params(params_file, edit_params)
    
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