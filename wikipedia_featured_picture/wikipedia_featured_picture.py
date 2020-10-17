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
username = os.getenv('wikipedia_picture_username')
password = os.getenv('wikipedia_picture_password')

previous_post_key = json_params['previous_post_key']

base_url = 'https://en.wikipedia.org/wiki/Template:POTD/'

today = date.today()

date = today.strftime("%Y-%m-%d")
date_url = date.replace(' ', '_')

# We do the check on the article URL
if previous_post_key == date_url:
    print("\n\n\nThere is nothing new to post\n\nDONE")
    exit(0)

# Setting the previous post key
json_params['previous_post_key'] = date_url

url = base_url + date

# Getting article itself
print("Downloading article")
today_article_page = requests.get(url)
today_article_soup = BeautifulSoup(today_article_page.content, 'html.parser')

# Getting article description
article_description_main_div = today_article_soup.find('div',{'style':'box-sizing: border-box; margin:0.5em; width: 600px; border: 3px #ccccff solid; padding: 11px; text-align: center; background-color: white;'})
full_article_description = article_description_main_div.text.replace('Archive – More featured pictures... ', '')

article_description = ''
photo_credit = ''

if 'Photograph credit:' in full_article_description:
    article_description = full_article_description.split('Photograph credit:')[0].strip()
    photo_credit = full_article_description.split('Photograph credit:')[1].split('Archive')[0].strip()
elif 'Engraving credit:' in full_article_description:
    article_description = full_article_description.split(('Engraving credit:'))[0].strip()
    photo_credit = full_article_description.split('Engraving credit:')[1].split('Archive')[0].strip()

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

time.sleep(20)

print("\n\nTransforming pdf in jpg")
pages = convert_from_path('latex/main.pdf', 500)
pages[0].save('out.jpg', 'JPEG')

time.sleep(20)

# Getting a better date
date = today.strftime("%B %d, %Y")

print(date)

# Setting caption
print('Setting full caption with date and hashtags')
hashtags = '#wikipedia #articleoftheday #bestoftheday'
full_caption = article_description + '\n\n' + date + '\n\nCredit: ' + photo_credit + '\n\n' + hashtags

print("Full caption:\n")
print(full_caption)
print()

time.sleep(10)

# In case instabot will stop working I can just change the following lines of 
# code, the previous ones can remain unchanged
print("Posting to instagram")
bot = Bot()
bot.login(username = username, password = password)
bot.upload_photo('out.jpg', caption = full_caption)

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
