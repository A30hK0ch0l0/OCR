import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from werkzeug.utils import secure_filename
from flask import Flask, request, flash, redirect, render_template, url_for
from flask import jsonify
import random
import configparser
import os
import core
from glob import glob

app = Flask(__name__)

app.secret_key = "secret key"

# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = 'static/data/'
CONFIG_FOLDER = 'configs'
# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'tif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_config():
    config_parser = configparser.ConfigParser()
    config_files = glob(f'{CONFIG_FOLDER}/*.cfg')
    config = {}
    for config_file in config_files:
        config_parser.read(config_file)
        # config = config_parser['resalat']
        for section in config_parser.sections():
            temp_conf = {}
            for k in config_parser[section].keys():
                if k == 'pdf_flag' or k == 'tesseract_flags_text' or k == 'tesseract_flags_title':
                    temp_conf[k] = config_parser[section][k]
                elif k == 'expand_title_box':
                    temp_conf[k] = float(config_parser[section][k])
                elif k == 'erase_area':
                    temp_conf[k] = eval(config_parser[section][k])
                else:
                    temp_conf[k] = int(config_parser[section][k])
            config[section] = temp_conf
    return config


all_configs = read_config()


@app.route('/')
def upload_form():
    return render_template('index.html')


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='data/' + filename), code=301)


@app.route('/pdf/', methods=['POST'])
def pdf():
    # print(request.values)
    file = request.files['file']
    newspaper_name = request.values['name']

    config = all_configs[newspaper_name]
    random_filename = random.getrandbits(128)
    # random_filename = newspaper_name + '_1400-4-9-'
    filename = secure_filename("{}.pdf".format(random_filename))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print('********', filepath)
    file.save(filepath)

    html_pages_results, json_pages_results = core.process_pdf(filepath, filename, config)
    return jsonify(html_pages_results, json_pages_results, filename)


if __name__ == "__main__":
    app.run(debug=True)
