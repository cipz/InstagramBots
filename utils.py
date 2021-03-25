
from pdf2image import convert_from_path

import urllib.request
import json
import os

# Average dominant color
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import PIL

# Accepts a string with the location of the params_file
# Returns a dictionary with the parameters
def get_params(params_file, username, password):
    
    params_dict = {}

    # Grabbing the username and password for the account
    with open(params_file) as params_file:
        json_params = json.load(params_file)

    params_file.close()

    # When testing locally with username and password in params file
    # params_dict['username'] = json_params['username']
    # params_dict['password'] = json_params['password']

    # When the username and password are stored as environment variables
    params_dict['username'] = os.getenv(username)
    params_dict['password'] = os.getenv(password)

    params_dict['previous_post_key'] = json_params['previous_post_key']

    return params_dict

# Accepts a dictionary with the edited params values
def set_params(params_file, edit_params):

    # Reading current parameters from file
    with open(params_file) as old_params_file:
        curr_params = json.load(old_params_file)
    old_params_file.close()

    # Debug print
    # print(curr_params)

    new_params = curr_params

    for key, value in edit_params.items():
        new_params[key] = value

    # Debug print
    # print(new_params)

    # Writing new params to file
    with open(params_file, 'w') as new_params_file:
        json.dump(new_params, new_params_file)
    new_params_file.close()

    return

# Accepts two strings, path where to download the image and the url from where to download the image
def download_image(img_path, img_url):

    f = open(img_path,'wb')
    f.write(urllib.request.urlopen(img_url).read())
    f.close()

    return

# Accepts two strings, path of input image and path of output image
def img_bg_color(input_img, output_img):

    # Getting average color in image and saving as background
    img = cv.imread(input_img)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_temp = img.copy()
    img_temp[:,:,0], img_temp[:,:,1], img_temp[:,:,2] = np.average(img, axis=(0,1))
    cv.imwrite(output_img, img_temp)

    return

def compile_xelatex_silent():

    os.system("\
        cd latex ; \
        xelatex main.tex >> /dev/null ; \
        xelatex main.tex >> /dev/null")

    return

def compile_xelatex_verbose():

    os.system("\
        cd latex ; \
        xelatex main.tex ; \
        xelatex main.tex")

    return

def compile_latex_silent():

    os.system("\
        cd latex ; \
        pdflatex main.tex >> /dev/null ; \
        pdflatex main.tex >> /dev/null")

    return

def compile_latex_verbose():

    os.system("\
        cd latex ; \
        pdflatex main.tex ; \
        pdflatex main.tex")

    return

def pdf_2_jpg(input_pdf, output_img):

    pages = convert_from_path(input_pdf, 500)
    pages[0].save(output_img, 'JPEG')

    return

