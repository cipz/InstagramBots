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
username = os.getenv('wikipedia_username')
password = os.getenv('wikipedia_password')

previous_post_key = json_params['previous_post_key']

file_base_url = 'https://upload.wikimedia.org/wikipedia/commons/'
base_url = 'https://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article/'

today = date.today()

date = today.strftime("%B %d, %Y")
date_url = date.replace(' ', '_')

url = base_url + date

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
json_params['previous_post_key'] = article_of_the_day_page_url

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
pages = convert_from_path('latex/main.pdf', 500)
pages[0].save('out.jpg', 'JPEG')

# Setting caption
print('Setting full caption with date and hashtags')
hashtags = '#wikipedia #articleoftheday #bestoftheday'
full_caption = article_description_text + '\n\n' + date + '\n\n' + hashtags

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
