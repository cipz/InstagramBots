# Instagram Bots

This repository contains a few python scripts that act as Instagram bots that scrape the Internet for interesting daily / weekly content.
It is not intended as a serious repository, it was created of of boredom and just for fun / entrataining reasons.

Sometimes they stop and the accounts need a password change since Facebook / Meta / Instagram does not like bots posting on their platform.
So there might be "service interruptions" from time to time.

## Last posts

- ![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cipz/InstagramBots/master/badges/starsfromnasa.json)
- ![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cipz/InstagramBots/master/badges/newyorkermagcovers.json)
- ![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cipz/InstagramBots/master/badges/wikipediaarticledaily.json)
- ![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cipz/InstagramBots/master/badges/wikipediapictureoftheday.json)
- ![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cipz/InstagramBots/master/badges/paroladelgiornozanichelli.json)
- ![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cipz/InstagramBots/master/badges/ilsantodioggi.json)

## The bots
Here is a list of the bots currently present in this repo:
- [astronomy_picture_of_the_day](https://www.instagram.com/starsfromnasa/): posts pictures from NASA's [APOD](https://apod.nasa.gov/apod/) website, which stands for ***A**stronomy **P**icture **O**f the **D**ay*;
- [the_new_yorker](https://www.instagram.com/newyorkermagcovers/): [The New Yorker](https://www.newyorker.com/magazine) mag covers;
- [wikipedia_featured_article](https://www.instagram.com/wikipediaarticledaily/): the picture of Wikipedia's [Today's featured article](https://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article) section;
- [wikipedia_featured_picture](https://www.instagram.com/wikipediapictureoftheday/): like the prvious one, but the focus is on the [Picture of the day](https://en.wikipedia.org/wiki/Wikipedia:Picture_of_the_day) page
- [zanichelli_parola_del_giorno](https://www.instagram.com/paroladelgiornozanichelli/): the [Zanichelli](http://dizionari.zanichelli.it/) is a famous italian dictionary which has a [word of the day section](https://dizionaripiu.zanichelli.it/cultura-e-attualita/le-parole-del-giorno/parola-del-giorno/);
- [santo_del_giorno](https://www.instagram.com/ilsantodioggi/): every day a new saint from [Santo del giorno](https://www.santodelgiorno.it/).

## How it works

The core of this project is [web scraping](https://en.wikipedia.org/wiki/Web_scraping).
Given a particular web page, each bot has the same behaviour:
1) it downloads the page
2) searches for the content in the page (text or image), possibly downloading it from other pages
3) a Latex file is compiled in order to create a square pdf (7cm x 7cm) which is then converted in `jpg`
4) sets the caption of the image and the hashtags
5) connects to Instagram and posts the picture with the caption

Each script can be executed by calling it inside it's folder (e.g. `python3 the_new_yorker.py`).
The `-d` or `--debug` argument can be used to test the script locally and avoid it posting on Instagram.
The `requirements.txt` file contains the python dependencies.

### Github Actions

In order to execute the scripts daily I have created a cron job in Github actions to execute all the bots.
This can be done in a more granular way, which means having a `yml` file for each script, but the initialization of the docker container used to compile the Latex files takes to much time compared to having them all execute together.

## Libraries and other dependencies

Here is a list of the main libraries used in this project:
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): for web scraping
- [PIL](https://pillow.readthedocs.io/en/stable/): for image editing / conversion
- [pdf2image](https://github.com/Belval/pdf2image) and [poppler-utils](https://pypi.org/project/python-poppler/): for converting the pdf files into jpg files
- [wget](https://pypi.org/project/wget/): for downloading content from the Internet

### Instagram API library

Currently, the Instagram API library used is [instagrapi](https://adw0rd.github.io/instagrapi/).
Such library contains API wrappers that have been reverse-engineered, thus not guaranteeing they will work forever.

### Latex figure creation and Docker container

A custom Docker container is initialized to execute the scripts.
This detaches the whole project from GitHub Action's containers and environments, allowing for better portability of the project (e.g. it can be executed the container even on a Raspberry Pi).

## Limitations
Unfortunately [the Facebook team](https://github.com/facebook) (who currently owns Instagram, among a thousand other things), does not like bots and other automated scripts that mess around with their data, so they frequently change APIs and block requests from third party libraries.
***[igbot](https://github.com/ohld/igbot/)*** and other libraries such as ***[instagram_private_api](https://github.com/ping/instagram_private_api/)*** are currently being blocked or not up to date with the APIs from FB.

## Improvements and possible future work

As said before, this repository is not intended as a too serious work, just a time-filling fun activity that allowed me to get acquainted with Instagram's APIs and other APIs from sites as Spotify, Google Trends and YouTube (even thouth there are no bots for them... yet!).

There are many improvements that can be done, here are just a few:
- avoid the use of Latex and use the PIL library to automatically generate the square images
- notification system when the bots fail
- badges with the latest post from each bot
- add Instagram stories and post videos
- make more granular `yml` workflow files, possibly one for each python script

## License

[MIT](https://opensource.org/licenses/MIT)

## Author

[Ciprian Voinea](https://www.linkedin.com/in/cvoinea/)
