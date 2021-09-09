from instagrapi import Client

def post_image(img_path, caption, username, password):

    cl = Client()
    cl.login(username, password)

    media = cl.photo_upload(img_path, caption = caption)

    return