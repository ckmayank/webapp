import os
import cv2
import numpy as np
import easyocr
from autocorrect import Speller
from flask import Flask, render_template, request, send_file, flash
from PIL import Image
from pyngrok import ngrok
app = Flask(__name__)
port_no=5000
ngrok.set_auth_token("2eVOEsPS8QzeXSojpgQeeDnDcuC_6uttugrnNTtzx1TMCz5f1")
public_url=ngrok.connect(port_no).public_url
app.route("/")
app.config['UPLOAD_FOLDER'] = 'uploads'

spell = Speller(lang='en')
reader = easyocr.Reader(['en'], gpu=False)

def ocr_process(image_path):
    if not os.path.exists(image_path):
        return '', 404

    nparr = np.fromfile(image_path, np.uint8)
    image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    processed_image = process_frame(image_np)
    text_results = reader.readtext(processed_image)

    corrected_text = ''
    for result in text_results:
        corrected_text += spell(result[1]) + '\n'

    return {'detected_text': corrected_text}

def process_frame(frame):
    pil_image = Image.fromarray(frame)
    gray_image = pil_image.convert('L')
    opencv_image = np.array(gray_image)

    return opencv_image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return '', 400

    file = request.files['file']
    if not file:
        return '', 400

    filename = 'capture.png'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    result = ocr_process(filepath)

    if not result:
        return '', 400

    os.remove(filepath)

    return result

if __name__ == '__main__':

    app.run(host='0.0.0.0',port=port_no)