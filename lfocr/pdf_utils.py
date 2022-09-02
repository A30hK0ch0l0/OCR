import os
import cv2
import numpy as np
from pdf2image import convert_from_path


# def remove_sections(read_path, flag, write_path):
#     try:
#         os.system("./gs -o ./tmp/{} -sDEVICE=pdfwrite {} {}".format(write_path, flag, read_path))
#         return True, ''
#     except Exception as e:
#         # print("pdf_tools.remove_sections: ", e)
#         return False, e


def convert_pdf_to_images(file_path, output_format='tif'):
    try:
        # file_path = os.path.join('tmp', file_name).replace('/static/data', '')
        # file_path = file_name
        pages = convert_from_path(file_path,
                                  320,
                                  use_pdftocairo=True,
                                  thread_count=100,
                                  fmt=output_format
                                  )
        # os.remove(file_path)
        images = []
        for page in pages:
            image = np.array(page)
            images.append(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return True, images
    except Exception as e:
        return False, e
