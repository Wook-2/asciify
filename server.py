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

# for checklist
requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1



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

##########

def handle_requests_by_batch():
    while True:
        requests_batch = []
        while not (len(requests_batch) >= BATCH_SIZE):
            try:
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue
            batch_outputs = []
            for request in requests_batch:
                batch_outputs.append(run(request['input'][0]))

            for request, output in zip(requests_batch, batch_outputs):
                request['output'] = output
                
threading.Thread(target=handle_requests_by_batch).start()


def run(file):
    
    image = PIL.Image.open(file).convert("RGB")
        
    asc_img = do(image)
    

    return [asc_img]




@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def asciify():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']

        try:
            PIL.Image.open(file).convert("RGB")
        except Exception: 
            return render_template('index.html', result = 'Import image please'), 400
        if file.filename == '':
            print('no file name')
            return redirect(request.url)

        if requests_queue.qsize() >= BATCH_SIZE:
            return render_template('index.html', result = 'TooMany requests try again'), 429

        req = {
            'input': [file]
        }
        requests_queue.put(req)

        while 'output' not in req:
            time.sleep(CHECK_INTERVAL)
        [res] = req['output']

        return render_template('index.html', result=res)
    
    return render_template('index.html')

### checklist 
@app.route('/healthz', methods=['GET'])
def checkHealth():
	return "Pong",200


@app.errorhandler(413)
def request_entity_too_large(error):
    return {'error': 'File Too Large'}, 413

if __name__ == '__main__':

    app.run(debug=False, port=8080, host='0.0.0.0')   
