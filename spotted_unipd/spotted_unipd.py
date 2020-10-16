from pdf2image import convert_from_path
from facebook_scraper import get_posts
from instabot import Bot
import json
import os
import re

fb_page_name = 'SpottedUnipd'

# Grabbing the username and password for the account
with open('_params.json', 'r') as params_file:
    json_params = json.load(params_file)

params_file.close()

# When testing locally with username and password in params file
username = json_params['username']
password = json_params['password']

# When the username and password are stored as environment variables
# username = os.getenv('spotted_username')
# password = os.getenv('spotted_password')

previous_post_key = json_params['previous_post_key']

# Retrieving posts from page
posts = []

tmp_posts = get_posts(fb_page_name, pages=20)
for post in tmp_posts:
    # print(post['post_id'])
    if post['post_id'] == previous_post_key:
        break
    else:
        posts.append(post)    

print(len(posts))

# The latest post in the page
json_params['previous_post_key'] = posts[0]['post_id']

print("There are", len(posts), " posts to convert to images and post to instagram")

if len(posts) == 0:
    print("There are no new posts")
    exit(0)

bot = Bot()
bot.login(username = username, password = password)

post_count = 0

for post in posts:

    post_count += 1
    
    print("Posting picture number", post_count)

    # print(post)

    # Setting caption for the post
    caption = post['post_id']

    # Removing emojis from the post content
    post_description = post['text']
    emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags=re.UNICODE)
    # print(emoji_pattern.sub(r'', post_description)) # no emoji

    print()

    # Saving post description in file
    post_description_file = open('latex/post_description.txt', 'r+')
    post_description_file.truncate(0)
    post_description = "\\newcommand{\PostDescription}{" + post_description + "}"
    post_description_file.write(post_description)
    post_description_file.close()

    print("\n\nCompliling tex file")
    # Twice because the first time it may not get the images' position correctly
    os.system("cd latex ; xelatex main.tex >> /dev/null ; xelatex main.tex >> /dev/null")
    # xelatex is very verbose and useful to test if / where an error occors
    # os.system("cd latex ; xelatex main.tex ; xelatex main.tex")
    
    print("\n\nTransforming pdf in jpg")
    pages = convert_from_path('latex/main.pdf', 500)
    pages[0].save('out.jpg', 'JPEG')

    # for testing purposes
    continue

    print("\n\nPosting to instagram")

    bot.upload_photo('out.jpg', caption = caption)

exit(0)

# Removing config folder from instabot
os.system('rm out.jpg')
os.system('rm *REMOVE_ME')
os.system('rm params.json')

with open('params.json', 'w') as new_params_file:
    json.dump(json_params, new_params_file)

params_file.close()

print("\n\nDONE")