import numpy as np
from lfocr import box_detection
from lfocr import box_utils
from lfocr import content_recognition
from lfocr import pdf_utils
from lfocr import statistical_analyse
from lfocr.newspapers_specific_process import *


def process_pdf(file_path, config):
    # print(config['pdf_flag'])
    # process_flag, e = pdf_utils.remove_sections(file_path, config['pdf_flag'], file_name)
    # if not process_flag:
    #     raise Exception("pdf_tools.remove_sections: ", e)

    process_flag, pages = pdf_utils.convert_pdf_to_images(file_path)
    if not process_flag:
        raise Exception("pdf_tools.convert_pdf_to_images: ", pages)

    if len(config['erase_area']) > 0:
        pages = erase_area(pages, config['erase_area'])

    html_pages_results = []
    json_pages_results = []
    for page_idx, image in enumerate(pages):
        # print(page_idx)

        # cv2.imwrite(('DATA/pdfs_output/{}_Page_{}.jpg'.format(file_name.split('.')[0], page_idx + 1)), image)
        title_boxes, text_boxes, image = box_detection.detect(image, config, path=False)
        new_text_boxes = box_utils.merge_boxes(text_boxes, config, box_type='text')
        merged_text_box, len_merged_text_box = box_utils.set_box_new_coordinates(new_text_boxes, config,
                                                                                 initial_idx=0,
                                                                                 box_type='text')

        new_title_boxes = box_utils.merge_boxes(title_boxes, config, box_type='title')
        merged_title_box, _ = box_utils.set_box_new_coordinates(new_title_boxes, config,
                                                                initial_idx=len_merged_text_box,
                                                                box_type='title')

        response = merged_text_box + merged_title_box

        all_merged_bbox = [list(map(int, box['coords'].split(','))) for box in response]
        picked_box_index = statistical_analyse.non_max_suppression_fast(np.array(all_merged_bbox))

        refine_response_text = []
        refine_response_title = []
        for res_idx, res in enumerate(response):

            if not (res['idx'] in picked_box_index):
                continue
            if res['title'] is True:
                text_response = content_recognition.title_recognition(res, image, config)
                refine_response_title.append(text_response)
            else:
                text_response = content_recognition.text_recognition(res, image, config)
                refine_response_text.append(text_response)

        refine_response_title = box_utils.remove_titles_based_on_len_thresholds(refine_response_title)

        refine_response_text = box_utils.remove_texts_based_on_len_thresholds(refine_response_text)
        refine_response_text, titles_news_pairs = box_utils.new_version_matching(refine_response_title,
                                                                                 refine_response_text, config)

        # refine_response = refine_response_text + refine_response_title

        json_pages_results.append({'page': 1 + page_idx, 'body': titles_news_pairs})
        # html_pages_results.append(render_template('index.html', filename=file_name, response=refine_response))

    return json_pages_results
