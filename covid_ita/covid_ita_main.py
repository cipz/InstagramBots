from babel.dates import format_datetime
from pdf2image import convert_from_path
from datetime import date
from instabot import Bot
from datetime import datetime
from PIL import Image, ImageDraw
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
username = os.getenv('covid_ita_main_username')
password = os.getenv('covid_ita_main_password')

previous_post_key = json_params['previous_post_key']

json_file = 'latest_data.json'
json_link = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json'

print("Downloading latest json")
f = open(json_file,'wb')
f.write(urllib.request.urlopen(json_link).read())
f.close()
print("json file downloaded")

print("Reading data from json")
with open(json_file) as f:
    json_data = json.load(f)

latest_post_date = json_data[-1:][0]['data']

print("Check if there is anything new to post")
if previous_post_key == latest_post_date:
    print("\n\n\nThere is nothing new to post\n\nDONE")
    exit(0)

# Setting the previous post key
json_params['previous_post_key'] = latest_post_date

today = json_data[-1:][0]
yesterday = json_data[-2:][0]

# Notes
caption_note = today['note']
if caption_note is not None:
    caption_note = today['note'] + '\n\n'
else:
    caption_note = ''

# Actual date of the data
caption_date = datetime.strptime(today['data'][:-9], '%Y-%m-%d')
caption_date = format_datetime(caption_date, 'dd LLLL yyyy', locale='it_IT')
caption_date_month = caption_date.split(' ')[1]
caption_date = caption_date.replace(caption_date_month, caption_date_month.capitalize())

hashtags = '#covid #italia #news #StayHomeSaveLives #covid19 #covidstatus #emergenzacovid #coronavirus #covid19italia #coronavirusitalia #virus #instavirus #instahealth #instahealthnews'

full_caption = 'Aggiornamento giornaliero del ' + caption_date + '.'\
    + '\n\nIl numero di nuovi contagi è ' + str(today['nuovi_positivi']) \
    + ' arrivando ad avere ' + str(today['totale_positivi']) + ' totale positivi.'\
    + '\n\n' \
    + hashtags

print('Caption\n')
print(full_caption)

print("\n\nSetting correct values in tex file")
words_file = open('latex/numbers.txt', 'r+')
words_file.truncate(0)

# line = ''
# words_file.write(line)

line = '\\newcommand{\\nuovipositivi}{' + str(today['nuovi_positivi']) + '}'
words_file.write(line)
line = '\\newcommand{\\totalipositivi}{' + str(today['totale_positivi']) + '}'
words_file.write(line)
line = '\\newcommand{\\totaleospitalizzati}{' + str(today['totale_ospedalizzati']) + '}'
words_file.write(line)
line = '\\newcommand{\\ricoveratisintomi}{' + str(today['ricoverati_con_sintomi']) + '}'
words_file.write(line)
line = '\\newcommand{\\terapiaintensiva}{' + str(today['terapia_intensiva']) + '}'
words_file.write(line)
line = '\\newcommand{\\dimessiguariti}{' + str(today['dimessi_guariti']) + '}'
words_file.write(line)
line = '\\newcommand{\\isolamento}{' + str(today['isolamento_domiciliare']) + '}'
words_file.write(line)
line = '\\newcommand{\\deceduti}{' + str(today['deceduti']) + '}'
words_file.write(line)
line = '\\newcommand{\\zona}{' + 'Italia' + '}'
words_file.write(line)
line = '\\newcommand{\\data}{' + caption_date + '}'
words_file.write(line)

words_file.close()

print("\n\nCompliling tex file")
# Twice because the first time it may not get the images' position correctly
#os.system("cd latex ; xelatex main.tex >> /dev/null ; xelatex main.tex >> /dev/null")
# pdflatex is very verbose and useful to test if / where an error occors
os.system("cd latex ; xelatex main.tex ; xelatex main.tex")

print("Waiting 20 seconds")
time.sleep(20)

print("\n\nTransforming pdf in jpg")
pages = convert_from_path('latex/main.pdf', 500)
pages[0].save('out.jpg', 'JPEG')

print("Waiting 10 seconds")
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