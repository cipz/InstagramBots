# Instagram Bots

This repository contains a few python scripts that act as Instagram bots that scrape the Internet for interesting daily / weekly content.
It is not intended as a serious repository, it was created of of boredom and just for fun / entrataining reasons.
The code is not well organized and there are no functions, it's just a bunch of scripts.

## The bots
Here is a list of the bots currently present in this repo:
- [astronomy_picture_of_the_day](https://www.instagram.com/starsfromnasa/): NASA has a website called [APOD](https://apod.nasa.gov/apod/), which stands for ***A**stronomy **P**icture **O**f the **D**ay*, this ~~little guy~~ bot (the first one I've done), posts the picture of the day, every day (unless it's a video or a gif, more in the [Limitations](#limitations) section)
- [the_new_yorker](https://www.instagram.com/newyorkermagcovers/): I like the covers of [The New Yorker](https://www.newyorker.com/magazine) (amazing weekly magazine) but there was no account with their covers. Now there is :)
- [wikipedia_featured_article](https://www.instagram.com/wikipediaarticledaily/): like NASA, Wikipedia has a [Today's featured article](https://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article) section from which i take the picture and description and post them to IG
- [wikipedia_featured_picture](https://www.instagram.com/wikipediapictureoftheday/): like the prvious one, but the focus is on the [Picture of the day](https://en.wikipedia.org/wiki/Wikipedia:Picture_of_the_day) page
- [zanichelli_parola_del_giorno](https://www.instagram.com/paroladelgiornozanichelli/): the [Zanichelli](http://dizionari.zanichelli.it/) is a famous italian dictionary which, you guessed it, has a [word of the day section](https://dizionaripiu.zanichelli.it/cultura-e-attualita/le-parole-del-giorno/parola-del-giorno/). I take the word and the meaning and post them in Instagram.
- [santo_del_giorno](https://www.instagram.com/ilsantodioggi/): every day a new saint from [Santo del giorno](https://www.santodelgiorno.it/)
- covid_ita: contains the scripts for 2 bots, one that posts pictures generated with coronavirus data and statistics taken from the [official repository of the Protezione Civile Italiana](https://github.com/pcm-dpc/COVID-19) for [the whole italian territory](https://www.instagram.com/covid_news_italia) and one that posts the data for each region. Here are the links to the accounts:

|[abruzzo](https://www.instagram.com/covid_news_abruzzo)|[friuli](https://www.instagram.com/covid_news_friuli)|[molise](https://www.instagram.com/covid_news_molise)|[toscana](https://www.instagram.com/covid_news_toscana)|[basilicata](https://www.instagram.com/covid_news_basilicata)|
| ------------- | ------------- | ------------- | ------------- | ------------- | 

|[lazio](https://www.instagram.com/covid_news_lazio)|[piemonte](https://www.instagram.com/covid_news_piemonte)|[trentino](https://www.instagram.com/covid_news_trentino)                     |[calabria](https://www.instagram.com/covid_news_calabria)|[liguria](https://www.instagram.com/covid_news_liguria)|
| ------------- | ------------- | ------------- | ------------- | ------------- | 

|[puglia](https://www.instagram.com/covid_news_puglia)|[umbria](https://www.instagram.com/covid_news_umbria)|[campania](https://www.instagram.com/covid_news_campania)|[lombardia](https://www.instagram.com/covid_news_lombardia)|[sardegna](https://www.instagram.com/covid_news_sardegna)|
| ------------- | ------------- | ------------- | ------------- | ------------- | 

|[valledaosta](https://www.instagram.com/covid_news_valledaosta)|[emiliaromagna](https://www.instagram.com/covid_news_emiliaromagna)|[marche](https://www.instagram.com/covid_news_marche)|[sicilia](https://www.instagram.com/covid_news_sicilia)|[veneto](https://www.instagram.com/covid_news_veneto)|
| ------------- | ------------- | ------------- | ------------- | ------------- | 

## How it works

The core of this project is [web scraping](https://en.wikipedia.org/wiki/Web_scraping).
Given a particular web page, each bot has the same behaviour:
1) it downloads the page
2) searches for the content in the page, possibly downloading it from other pages
3) a latex file is compiled in order to create a square pdf (7cm x 7cm) which is then converted in jpg
4) sets the caption of the image and the hashtags
5) connects to Instagram and posts the picture with the caption

### Github Actions

In order to execute the scripts daily I have created a cron job in Github actions that runs at least twice a day to execute all the bots.
This can be done in a more granular form, which means having a `yml` file for each script, but the installation of latex takes to much time and it's not worth it as of this moment.

## Libraries and other dependencies

Here is a list of the main libraries used in this project:
- [instabot](https://github.com/ohld/igbot/): third party APIs for posting content to Instagram
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): for web scraping
- [PIL](https://pillow.readthedocs.io/en/stable/): for image editing / conversion
- [pdf2image](https://github.com/Belval/pdf2image) and [poppler-utils](https://pypi.org/project/python-poppler/): for converting the pdf files into jpg files
- [wget](https://pypi.org/project/wget/): for downloading content from the Internet

## Limitations
Unfortunately [the Facebook team](https://github.com/facebook) (who currently owns Instagram, among a thousand other things), does not like bots nor developers or amateur coders that want to do simple projects like this one, so they always change APIs and block requests from third party libraries.
***[igbot](https://github.com/ohld/igbot/)*** and other libraries such as ***[instagram_private_api](https://github.com/ping/instagram_private_api/)*** are currently being blocked or are not up to date with the APIs from FB.

## Improvements and possible future work

As I said before, this repository is not intended as a serious work, just a time-filling fun activity that allowed me to get acquainted with Instagram's APIs and other APIs from sites as Spotify, Google Trends and YouTube (even thouth there are no bots for them... yet!).

There are many improvements that can be done, here are just a few:
- create a single `utils.py` file that contains the common functions
- avoid the use of latex and use the PIL library to automatically generate the square images
- make more granular `yml` workflow files, possibly one for each python script
