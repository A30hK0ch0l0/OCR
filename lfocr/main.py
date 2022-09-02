import json
import configparser
from .core import process_pdf
from glob import glob
import os


class ocr():

    def __init__(self):
        self.config_folder = f'{os.path.dirname(os.path.abspath(__file__))}/data/configs'
        self.configs = self.read_config()
        # print(self.configs)

    def read_config(self):
        config_parser = configparser.ConfigParser()
        config_files = glob(f'{self.config_folder}/*.cfg')
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

    def process(self, path, name):
        json_result = process_pdf(path, self.configs[name])
        return json_result
