from instabot import Bot
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
import requests
import wget
import time
import json
import os

# Grabbing the username and password for the account
with open('params.json', 'r') as params_file:
    json_params = json.load(params_file)

params_file.close()

# When testing locally with username and password in params file
# username = json_params['username']
# password = json_params['password']

# When the username and password are stored as environment variables
username = os.getenv('zanichelli_username')
password = os.getenv('zanichelli_password')

previous_post_key = json_params['previous_post_key']

print("Setting url and downloading content")
url = 'https://dizionaripiu.zanichelli.it/cultura-e-attualita/le-parole-del-giorno/parola-del-giorno/'

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

parola_title = soup.find('header', {'class':'mb-4'}).text.strip()
sillabazione = soup.find('span', {'style':'display: block; margin-left: 00pt; text-indent: -00pt;'}).text.replace('SINONIMI','').replace('SILLABAZIONE:','').strip()
tipologia_parola = soup.find('span', {'style':'display: block; margin-left: 12pt; text-indent: -06pt;'}).text.strip()
significati_parola = soup.findAll('span', {'style':'display: block; margin-left: 24pt; text-indent: -06pt;'})
origine_parola = significati_parola[0].text
significati_parola = significati_parola[1:]
data = soup.find('div', {'class':'article-meta col text-right'}).text

# Checking word
if previous_post_key != "" and previous_post_key == parola_title:
    print("\n\n\nThere is nothing new to post\n\nDONE")
    exit(0)

json_params['previous_post_key'] = parola_title

caption_significati = ''
for i in significati_parola:
    if len(caption_significati) > 1600:
        break
    caption_significati += '\n' + i.text

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
# Twice because the first time it may not get the images' position correctly
os.system("cd latex ; xelatex main.tex >> /dev/null ; xelatex main.tex >> /dev/null")
# pdflatex is very verbose and useful to test if / where an error occors
# os.system("cd latex ; xelatex main.tex ; xelatex main.tex")
 
# Wait for the pdf to be correctly created
print('Waiting for the pdf to be correctly created')
time.sleep(20)

print("\n\nTransforming pdf in jpg")
pages = convert_from_path('latex/main.pdf', 500)
pages[0].save('out.jpg', 'JPEG')

# Wait for the img to be converted
print('Wait for the img to be converted')
time.sleep(10)

print("\n\nPosting to instagram")
bot = Bot()
bot.login(username = username, password = password)
bot.upload_photo('out.jpg', caption = caption)
bot.logout()

# Removing config folder from instabot
# os.system('rm "' + str(img_download) + '"')
os.system('rm img.jpg')
os.system('rm out.jpg')
os.system('rm *REMOVE_ME')
os.system('rm params.json')

with open('params.json', 'w') as new_params_file:
    json.dump(json_params, new_params_file)

params_file.close()

print("\n\nDONE")
