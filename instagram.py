from instabot import Bot

def post_image(img_path, caption, username, password):

    bot = Bot()
    bot.login(username = username, password = password)
    bot.upload_photo(img_path, caption = caption)
    bot.logout()

    return