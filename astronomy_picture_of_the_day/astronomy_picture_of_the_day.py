from pdf2image import convert_from_path
from bs4 import BeautifulSoup
from instabot import Bot
from datetime import date
import requests
import wget
import json
import os

# TODO https://stackoverflow.com/questions/3241929/python-find-dominant-most-common-color-in-an-image

# Grabbing the username and password for the account
with open('params.json', 'r') as params_file:
    json_params = json.load(params_file)

params_file.close()

# When testing locally with username and password in params file
# username = json_params['username']
# password = json_params['password']

# When the username and password are stored as environment variables
username = os.getenv('apod_username')
password = os.getenv('apod_password')

previous_post_key = json_params['previous_post_key']

base_url = 'https://apod.nasa.gov/apod/'

# today = date.today()
# today_url = 'ap' + today.strftime("%y%m%d") + '.html'
# url = base_url + today_url

url = base_url

page = requests.get(url)

# print(page)

soup = BeautifulSoup(page.content, 'html.parser')

img_name = soup.findAll(name='b')[0].text.strip()
img_credit = soup.findAll(name='a')[3].text.strip()

if previous_post_key != "" and previous_post_key == img_name:
    print("\n\n\nThere is nothing new to post\n\nDONE")
    exit(0)

json_params['previous_post_key'] = img_name

img_tag = soup.findAll(name='img')[0]
img_src = img_tag['src']
img_url = base_url + img_src
img_download = wget.download(img_url)

# Renaming image file to be used in the latex file
os.system('mv ' + img_download + ' img.jpg')

print("\n\nCompliling tex file")
# Twice because the first time it may not get the images' position correctly
os.system("cd latex ; pdflatex main.tex >> /dev/null ; pdflatex main.tex >> /dev/null")
# pdflatex is very verbose and useful to test if / where an error occors
# os.system("cd latex ; pdflatex main.tex ; pdflatex main.tex")

print("\n\nTransforming pdf in jpg")
pages = convert_from_path('latex/main.pdf', 500)
pages[0].save('out.jpg', 'JPEG')

par_tag = soup.findAll(name='p')
caption = par_tag[2]

# The caption paragraph contains another p
# that needs to be removed
for p in caption.findAll(name='p'):
    p.extract() 

if(len(caption.findAll(name='b')) > 0):
    caption.findAll(name='b')[0].extract() 

hashtags = '#stars #nasa #astronomy #apod #dailyposting'
caption = img_name + ' (by ' + img_credit + ')' + '\n\n' + caption.text.replace('\n', ' ').replace('  ', ' ').strip() + '\n\n' + hashtags

print('Caption:\n\n')
print(caption)
print()

print("\n\nPosting to instagram")
bot = Bot()
bot.login(username = username, password = password)
bot.upload_photo('out.jpg', caption = caption)

# Removing config folder from instabot
# os.system('rm "' + str(img_name) + '"')
os.system('rm img.jpg')
os.system('rm out.jpg')
os.system('rm *REMOVE_ME')
os.system('rm params.json')

with open('params.json', 'w') as new_params_file:
    json.dump(json_params, new_params_file)

params_file.close()

print("\n\nDONE")