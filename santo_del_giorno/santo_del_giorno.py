from pdf2image import convert_from_path
from datetime import date
from instabot import Bot
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup
import urllib.request
import requests
import time
import wget
import json
import os

# Grabbing the username and password for the account
with open('params.json') as params_file:
    json_params = json.load(params_file)

params_file.close()

# When testing locally with username and password in params file
# username = json_params['username']
# password = json_params['password']

# When the username and password are stored as environment variables
username = os.getenv('santo_username')
password = os.getenv('santo_password')

previous_post_key = json_params['previous_post_key']

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
json_params['previous_post_key'] = giorno

today_main_div = today_article_soup.find('div', {'id':'CenterDiv'})
santo_url = today_main_div.find('a')['href']

url = base_url + santo_url

santo_main_page = requests.get(url)
santo_main_page_soup =  BeautifulSoup(santo_main_page.content, 'html.parser')

santo_main_div = santo_main_page_soup.find('div', {'id':'CenterDiv'})

nome_santo = santo_main_div.find('h1').text
foto_santo_url = santo_main_div.find('img')['src']
descrizione_santo = santo_main_div.find('div',{'style':'float:left; text-align:justify; width: 512px;margin-left: 30px;'})

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

    new_caption = new_caption + '.'

    coda = '\n\nPer la descrizione completa continuare su \'santodelgiorno.it\''
    new_caption = new_caption.strip() + coda

if len(new_caption) > 0:
    caption = new_caption

hashtags = '#santo #chiesa #cristo #cristianesimo'

today = date.today()
anno = today.strftime("%Y")

giorno_caption = giorno.replace('Oggi','').replace('si venera:','').strip() + ' ' + anno
full_caption = nome_santo + '\n\n' + caption + '\n\n' + giorno_caption + '\n\n' + hashtags

print(full_caption)

image_link = base_url + foto_santo_url

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

# time.sleep(20)

print("\n\nTransforming pdf in jpg")
pages = convert_from_path('latex/main.pdf', 500)
pages[0].save('out.jpg', 'JPEG')

# In case instabot will stop working I can just change the following lines of 
# code, the previous ones can remain unchanged
print("Posting to instagram")
bot = Bot()
bot.login(username = username, password = password)
bot.upload_photo('out.jpg', caption = full_caption)
bot.logout()

# Removing stuff (not necessary if used in docker container of github actions)
print("Removing unused files")
os.system('rm "' + image_file + '"')
os.system('rm *REMOVE_ME')
os.system('rm img.jpg')
os.system('rm out.jpg')
os.system('rm params.json')

with open('params.json', 'w') as new_params_file:
    json.dump(json_params, new_params_file)

params_file.close()

print("\nDONE")