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
    params = utils.get_params(params_file, 'wikipedia_username', 'wikipedia_password')

    username = params['username']
    password = params['password']
    previous_post_key = params['previous_post_key']

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Defining edited parameters dictionary
    edit_params = {}

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Custom part of the bot

    file_base_url = 'https://upload.wikimedia.org/wikipedia/commons/'
    base_url = 'https://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article/'

    # Does not work otherwise, will look into it 
    from datetime import date
    today = date.today()

    date = today.strftime("%B %d, %Y")
    date_url = str(date).replace(' 0', ' ').replace(' ', '_')

    url = base_url + date_url

    # Getting article itself
    print("Downloading article")
    today_article_page = requests.get(url)
    today_article_soup = BeautifulSoup(today_article_page.content, 'html.parser')

    # Getting article description
    article_description = today_article_soup.find('div',{'class':'mw-parser-output'}).find('p')
    article_description_text = article_description.text.replace('(Full article...)','').strip()

    # Getting article main url to get picture
    article_of_the_day_page_url = article_description.find('a')['href']

    # We do the check on the article URL
    if previous_post_key != "" and previous_post_key == article_of_the_day_page_url:
        print("\n\n\nThere is nothing new to post\n\nDONE")
        exit(0)

    # Setting the previous post key
    edit_params['previous_post_key'] = article_of_the_day_page_url

    print('New article URL:', article_of_the_day_page_url)

    article_base_url = 'https://en.wikipedia.org'
    article_complete_url = article_base_url + article_of_the_day_page_url

    article_page = requests.get(article_complete_url)
    article_page_soup = BeautifulSoup(article_page.content, 'html.parser')

    article_page_image_url = article_page_soup.findAll('meta', {'property':'og:image'})[0]['content']
    image_ext = article_page_image_url[-4:]
    image_file = 'img' + image_ext

    print("Downloading image")
    f = open(image_file,'wb')
    f.write(urllib.request.urlopen(article_page_image_url).read())
    f.close()
    print("Image downloaded")

    print("\n\nCompliling tex file")
    # Twice because the first time it may not get the images' position correctly
    os.system("cd latex ; pdflatex main.tex >> /dev/null ; pdflatex main.tex >> /dev/null")
    # pdflatex is very verbose and useful to test if / where an error occors
    # os.system("cd latex ; pdflatex main.tex ; pdflatex main.tex")

    print("\n\nTransforming pdf in jpg")
    utils.pdf_2_jpg('latex/main.pdf', 'out.jpg')

    # Setting caption
    print('Setting full caption with date and hashtags')
    hashtags = '#wikipedia #articleoftheday #bestoftheday'
    full_caption = article_description_text + '\n\n' + date + '\n\n' + hashtags

    print("Full caption:\n")
    print(full_caption)
    print()

    if not debug:

        execution_result = {}
        execution_result["color"] =  "green"

        try:

            print("Posting to instagram")
            instagram.post_image('out.jpg', full_caption, username, password)

        except Exception as e:

            execution_result["color"] =  "red"

        utils.edit_badge("wikipediaarticledaily.json", execution_result)

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