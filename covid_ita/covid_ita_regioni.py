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

# Lista delle regioni
regioni = [
        ['abruzzo', '13'],
        ['basilicata', '17'],
        ['bolzano', '21'],
        ['calabria', '18'],
        ['campania', '15'],
        ['emiliaromagna', '8'],
        ['friuli', '6'],
        ['lazio', '12'],
        ['liguria', '7'],
        ['lombardia', '3'],
        ['marche', '11'],
        ['molise', '14'],
        ['piemonte', '1'],
        ['puglia', '16'],
        ['sardegna', '20'],
        ['sicilia', '19'],
        ['toscana', '9'],
        ['trentino', '22'],
        ['umbria', '10'],
        ['valledaosta', '2'],
        ['veneto', '5']
    ]

# Grabbing the username and password for the account
with open('params_regioni.json') as params_file:
    json_params = json.load(params_file)

params_file.close()

previous_post_key = json_params['previous_post_key']

json_file = 'latest_data.json'
json_link = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json'

print("Downloading latest json")
f = open(json_file,'wb')
f.write(urllib.request.urlopen(json_link).read())
f.close()
print("json file downloaded")

print("Reading data from json")
with open(json_file) as f:
    json_data = json.load(f)

# for i in json_data:
#     print(i['denominazione_regione'], i['codice_regione'])

latest_post_date = json_data[-1:][0]['data']

print("Check if there is anything new to post")
if previous_post_key == latest_post_date:
    print("\n\n\nThere is nothing new to post\n\nDONE")
    exit(0)

# Setting the previous post key
json_params['previous_post_key'] = latest_post_date

# Actual date of the data
caption_date = datetime.strptime(latest_post_date[:-9], '%Y-%m-%d')
caption_date = format_datetime(caption_date, 'dd LLLL yyyy', locale='it_IT')
caption_date_month = caption_date.split(' ')[1]
caption_date = caption_date.replace(caption_date_month, caption_date_month.capitalize())

hashtags = '#covid #italia #news #StayHomeSaveLives #covid19 #covidstatus #emergenzacovid #coronavirus #covid19italia #coronavirusitalia #virus #instavirus #instahealth #instahealthnews'

for nome_regione, codice_regione in regioni:
    
    print('\n\nCreating post for', nome_regione, codice_regione)
    
    username = os.getenv('covid_ita_' + nome_regione + '_username')
    password = os.getenv('covid_ita_' + nome_regione + '_password')

    if username is None or password is None:
        print('username or password not available for', nome_regione)
        continue

    regione = None
    for r in json_data:
        # print(r['codice_regione'])
        # print(codice_regione)
        if str(r['codice_regione']) == str(codice_regione):
            regione = r
            print(r)
            break

    # print(nome_regione)
    # print(regione['denominazione_regione'])

    # Notes
    caption_note = regione['note']
    if caption_note is not None:
        caption_note = regione['note'] + '\n\n'
    else:
        caption_note = ''

    full_caption = 'Aggiornamento giornaliero del ' + caption_date + '.'\
        + '\n\nIl numero di nuovi contagi è ' + str(regione['nuovi_positivi']) \
        + ' arrivando ad avere ' + str(regione['totale_positivi']) + ' totale positivi.'\
        + '\n\n' \
        + hashtags

    # TODO aggiungere hashtags specifici per ciascuna regione

    print('Caption\n')
    print(full_caption)

    print("\n\nSetting correct values in tex file")
    words_file = open('latex/numbers.txt', 'r+')
    words_file.truncate(0)

    # line = ''
    # words_file.write(line)

    line = '\\newcommand{\\nuovipositivi}{' + str(regione['nuovi_positivi']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\totalipositivi}{' + str(regione['totale_positivi']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\totaleospitalizzati}{' + str(regione['totale_ospedalizzati']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\ricoveratisintomi}{' + str(regione['ricoverati_con_sintomi']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\terapiaintensiva}{' + str(regione['terapia_intensiva']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\dimessiguariti}{' + str(regione['dimessi_guariti']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\isolamento}{' + str(regione['isolamento_domiciliare']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\deceduti}{' + str(regione['deceduti']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\zonanome}{' + str(regione['denominazione_regione']) + '}'
    words_file.write(line)
    line = '\\newcommand{\\zonaimg}{' + nome_regione + '}'
    words_file.write(line)
    line = '\\newcommand{\\data}{' + caption_date + '}'
    words_file.write(line)

    words_file.close()

    print("\n\nCompliling tex file")
    # Twice because the first time it may not get the images' position correctly
    os.system("cd latex ; xelatex main.tex >> /dev/null ; xelatex main.tex >> /dev/null")
    # pdflatex is very verbose and useful to test if / where an error occors
    # os.system("cd latex ; xelatex main.tex ; xelatex main.tex")

    # print("Waiting 20 seconds")
    # time.sleep(20)

    print("\n\nTransforming pdf in jpg")
    pages = convert_from_path('latex/main.pdf', 500)
    pages[0].save('out.jpg', 'JPEG')

    print("Waiting 10 seconds")
    time.sleep(10)


    # In case instabot will stop working I can just change the following lines of 
    # code, the previous ones can remain unchanged
    print("Posting to instagram")
    try:
        
        # Initializing instagram bot
        bot = Bot()
        
        bot.login(username = username, password = password)
        bot.upload_photo('out.jpg', caption = full_caption)
        
        # Removing stuff (not necessary if used in docker container of github actions)
        print("Removing unused files")
        os.system('rm *REMOVE_ME')
        os.system('rm img.jpg')
        os.system('rm out.jpg')
        os.system('rm params.json')

    except:

        print('An error has occoured while posting to instagram for ', nome_regione)

    with open('params.json', 'w') as new_params_file:
        json.dump(json_params, new_params_file)

    params_file.close()

    print()
    print("Waiting 10 seconds before creating post for new region")
    time.sleep(10)

print("\nDONE")
