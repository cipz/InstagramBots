#!/usr/bin/python

# Importing custom files
import sys
sys.path.insert(1, '../')

import utils
import instagram

from itertools import cycle
from datetime import date
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup
import urllib.request
import requests
import praw
import time
import wget
import json
import os
import re

def main(debug):
    
    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Getting parameters
    username = os.getenv("reddit_username")
    password = os.getenv("reddit_password")

    params_file = 'params.json'

    with open(params_file) as params_file:
        json_params = json.load(params_file)
    params_file.close()

    # previous_post_key is the last subreddit that has had a meme posted
    previous_post_key = json_params['previous_post_key']

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    # Defining edited parameters dictionary
    edit_params = {}
    edit_params = json_params

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 

    ### SETTING THE NEW SUBREDDIT ###

    # Getting list of subreddits

    subreddits = list(json_params["subreddits"].keys())
    circular_subreddits = cycle(subreddits)
    
    # Find if there's a way to get the next of a given parameter in the cycle
    tmp = next(circular_subreddits)
    while tmp != previous_post_key:
        tmp = next(circular_subreddits)

    new_subreddit = next(circular_subreddits)

    # Setting the previous post key
    edit_params['previous_post_key'] = new_subreddit

    old_post_id = json_params["subreddits"][new_subreddit]
    
    ### CONNECTING TO REDDIT ###

    reddit_params = os.getenv("reddit_params")
    reddit_params = json.loads(reddit_params)

    r = praw.Reddit(client_id=reddit_params["client_id"],           
                    client_secret=reddit_params["client_secret"],   
                    user_agent=reddit_params["user_agent"],         
                    username=reddit_params["username"],             
                    password=reddit_params["password"])             
                    
    subreddit = r.subreddit(new_subreddit)

    # Getting the top 10 posts of the day
    posts = list(subreddit.top("day"))[:10]

    ### Understanding which

    tmp_index = -1
    found = False
    while not found:
        
        tmp_index += 1
        
        url = posts[tmp_index].url
        file_name = url.split("/")

        if len(file_name) == 0:
            file_name = re.findall("/(.*?)", url)

        file_name = file_name[-1]

        # The post does not have an image attached
        if "." not in file_name:
            continue

        print("NEW", posts[tmp_index].id)
        print("OLD", old_post_id)

        print()

        if posts[tmp_index].id == old_post_id:
            continue
        
        # The post contains a gif
        if (file_name.split(".")[1]) == "gif":
            continue 

        found = True

    new_post_index = tmp_index

    ### Getting the parameters from the post ###

    # I actually want to work on one post only
    post = posts[new_post_index]

    # Submission attributes
    # https://praw.readthedocs.io/en/latest/code_overview/models/submission.html
    
    url = post.url

    file_name = url.split("/")

    if len(file_name) == 0:
        file_name = re.findall("/(.*?)", url)

    file_name = file_name[-1]

    r = requests.get(url)

    file_name = "img" + "." + file_name.split(".")[1]

    with open(file_name,"wb") as f:
        f.write(r.content)

    ### Setting caption ###

    hashtags = "#meme #memes #fun #bot #reddit" +\
               " #" + new_subreddit

    full_caption = post.title + \
        "\n\n" +\
        "Posted by /u/" + str(post.author) + " in /r/" + new_subreddit +\
        "\n\n" +\
        hashtags

    print(full_caption, "\n\n")

    edit_params["subreddits"][new_subreddit] = post.id

    print(edit_params, "\n\n")

    ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- ## -- 
    
    # Getting average color in image and saving as background
    print("Setting bakground color")
    utils.img_bg_color(file_name, 'bg.jpg')
    
    print("\n\nCompliling tex file")
    if debug:
        utils.compile_latex_verbose()
    else:
        utils.compile_latex_silent()
    
    print("\n\nTransforming pdf in jpg")
    utils.pdf_2_jpg('latex/main.pdf', 'out.jpg')

    if not debug:

        # print("Posting to instagram")
        instagram.post_image('out.jpg', full_caption, username, password)
    
        print('Setting new parameters')
        with open('params.json', 'w') as f:
            json.dump(edit_params, f)

        # Removing stuff (not necessary if used in docker container of github actions)
        # In case of local it could be userful
        print("Removing unused files")
        os.system('rm *REMOVE_ME')
        os.system('rm ' + file_name)
        os.system('rm out.jpg')   
        os.system('rm bg.jpg')   

if __name__ == "__main__":

    if "--debug" in sys.argv[1:]:
        debug=True
    elif "-d" in sys.argv[1:]:
        debug=True
    else:
        debug=False

    main(debug)

    print("\nDONE")