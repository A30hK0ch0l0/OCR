import math
import os

import pytesseract

from lfocr.image_utils import remove_noise_and_smooth


def recognition(img, is_title, config, lang='life0005'):
    img = remove_noise_and_smooth(img)
    model_path = f'{os.path.dirname(os.path.abspath(__file__))}/data/tesseract/'
    model_flag = fr' --tessdata-dir "{model_path}"'
    # Recognize the text as string in image using pytesserct
    if is_title:
        flags = config['tesseract_flags_title'] + model_flag
    else:
        flags = config['tesseract_flags_text'] + model_flag
    text = pytesseract.image_to_string(img, lang=lang, config=flags)

    # Remove empty lines of text - s.strip() removes lines with spaces
    text = os.linesep.join([s for s in text.splitlines() if s.strip()])

    return text


def title_recognition(sample, image, config):
    expand = int(sample['h'] * config['expand_title_box'])

    coords = "{},{},{},{}".format(sample['x'], sample['y'] - expand, sample['x'] + sample['w'],
                                  sample['y'] + sample['h'] + expand)
    data = image[sample['y'] - expand:sample['y'] + sample['h'] + expand, sample['x']:sample['x'] + sample['w']]
    # cv2.imwrite('DATA/cropped/_{}.jpg'.format(res_idx), data)

    result = recognition(data, sample['title'], config)
    sample['text'] = result
    sample['coords'] = coords
    return sample


def text_recognition(sample, image, config):
    line_height = sample['h'] / sample['lines_count']
    text = ''
    for idx in range(sample['lines_count']):
        start_y = int(math.ceil(idx * line_height + sample['y']))
        end_y = int(math.ceil((idx + 1) * line_height + sample['y'])) + 1
        data = image[start_y:end_y, sample['x']:sample['x'] + sample['w']]
        # result = ''
        result = recognition(data, sample['title'], config)
        text = text + result + '\n'
    sample['text'] = text

    return sample
