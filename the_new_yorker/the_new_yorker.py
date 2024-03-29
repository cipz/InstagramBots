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
    params = utils.get_params(params_file, 'the_new_yorker_username', 'the_new_yorker_password')

    username = params['username']
    password = params['password']
    previous_post_key = params['previous_post_key']

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Defining edited parameters dictionary
    edit_params = {}

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Getting main page
    url = 'https://www.newyorker.com/magazine'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    cover_div = soup.find('div', {'class':'MagazineCover__cover___2bDZf'})
    issue_link = cover_div.find('a')['href']

    current_issue_date = soup.find('div', {'class':'MagazineHeader__header___2wMTg'}).find('h2').text.strip()
    current_issue_title = soup.find('figcaption').text.strip()

    # Getting full res picture
    issue_page = requests.get(issue_link)
    issue_soup = BeautifulSoup(issue_page.content, 'html.parser')
    issue_main_content = issue_soup.find('main', {'id':'main-content'})
    img_link = issue_main_content.find('img', {'class':'responsive-image__image'})['src']

    if previous_post_key != "" and previous_post_key == current_issue_date:
        print("\n\n\nThere is nothing new to post\n\nDONE")
        exit(0)

    edit_params['previous_post_key'] = current_issue_date

    # Setting caption
    print("Setting caption")
    hashtags = 'Follow our page to get the new cover every week!\nFor more follow @newyorkermag\n\n#thenewyorker #magazine #newyorkermag'
    full_caption = current_issue_title + '\n\n' + current_issue_date + '\n\n' + hashtags

    print("CAPTION:", full_caption)

    print("Downloading image")
    img_download = wget.download(img_link)

    # Renaming image file to be used in the latex file
    os.system('mv ' + img_download + ' img.jpg')

    print("\n\nCompliling tex file")
    # utils.compile_latex_verbose()
    utils.compile_latex_silent()
    
    # Wait for the pdf to be correctly created
    print('Waiting for the pdf to be correctly created')
    time.sleep(20)

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

        utils.edit_badge("newyorkermagcovers.json", execution_result)

        # Removing stuff (not necessary if used in docker container of github actions)
        # Useful if executed locally
        print("Removing useless files")
        os.system('rm out.jpg')
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