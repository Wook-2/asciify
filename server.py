import PIL
from PIL import Image
import sys
import urllib.request
from flask import Flask, request, send_file, flash, redirect, render_template, url_for, jsonify
import numpy as np
import time
import threading
import io
from queue import Queue, Empty

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 8



ASCII_CHARS = ['.',',',':',';','+','*','?','%','S','#','@']
ASCII_CHARS = ASCII_CHARS[::-1]

'''
method resize():
    - takes as parameters the image, and the final width
    - resizes the image into the final width while maintaining aspect ratio
'''
def resize(image, new_width=100):
    (old_width, old_height) = image.size
    aspect_ratio = float(old_height)/float(old_width)
    new_height = int(aspect_ratio * new_width)
    new_dim = (new_width, new_height)
    new_image = image.resize(new_dim)
    return new_image
'''
method grayscalify():
    - takes an image as a parameter
    - returns the grayscale version of image
'''
def grayscalify(image):
    return image.convert('L')

'''
method modify():
    - replaces every pixel with a character whose intensity is similar
'''
def modify(image, buckets=25):
    initial_pixels = list(image.getdata())
    new_pixels = [ASCII_CHARS[pixel_value//buckets] for pixel_value in initial_pixels]
    return ''.join(new_pixels)

'''
method do():
    - does all the work by calling all the above functions
'''
def do(image, new_width=100):
    image = resize(image)
    image = grayscalify(image)

    pixels = modify(image)
    len_pixels = len(pixels)

    # Construct the image from the character list
    new_image = [pixels[index:index+new_width] for index in range(0, len_pixels, new_width)]

    return '\n'.join(new_image)

'''
method runner():
    - takes as parameter the image path and runs the above code
    - handles exceptions as well
    - provides alternative output options
'''
def runner(path):
    image = None
    try:
        image = Image.open(path)
    except Exception:
        print("Unable to find image in",path)
        #print(e)
        return
    image = do(image)

    # To print on console
    print(image)

    # Else, to write into a file
    # Note: This text file will be created by default under
    #       the same directory as this python file,
    #       NOT in the directory from where the image is pulled.
    f = open('img.txt','w')
    f.write(image)
    f.close()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def asciify():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            print('no file name')
            return redirect(request.url)
        
        image = PIL.Image.open(file).convert("RGB")
        
        asc_img = do(image)
        # print(asc_img)

        return render_template('index.html', result=asc_img)
    
    return render_template('index.html')
        
if __name__ == '__main__':

    app.run(debug=True, port=8080, host='0.0.0.0')   
