import cv2
import numpy as np

from lfocr import image_utils


def detect(image_file_name, config, path):
    image = np.array(image_file_name)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    processed_image = image_utils.remove_box_lines(image, config)
    # cv2.imwrite('3_line_image_clean_thresh.jpg', processed_image)

    # search the phrases
    processed_image_filled = image_utils.find_phrase(processed_image, config)

    contours, _ = cv2.findContours(processed_image_filled, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    refined_contours = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h < config['h']:
            continue
        refined_contours.append(cnt)

    kernel = np.ones((config['kernel_row'], config['kernel_col']), np.uint8)

    title_boxes = []
    text_boxes = []
    for idx, cnt in enumerate(refined_contours):
        x, y, w, h = cv2.boundingRect(cnt)

        cropped_part = processed_image[y:y + h, x:x + w]
        erosion_output = cv2.erode(cropped_part, kernel, iterations=1)
        is_text = sum(sum(erosion_output))
        # print(w*h)
        if is_text != 0:
            coords = "{},{},{},{}".format(x, y, x + w, y + h)
            title_boxes.append({'x': x, 'y': y, 'w': w, 'h': h,
                                'idx': idx, 'title': True, 'vis': True,
                                'coords': coords})
            # cv2.imwrite('DATA/cropped/__{}.jpg'.format(idx), image[y:y + h, x:x + w])

        else:
            if h * w < 1000:
                continue
            coords = "{},{},{},{}".format(x, y, x + w, y + h)
            text_boxes.append({'x': x, 'y': y, 'w': w, 'h': h,
                               'idx': idx, 'title': False, 'vis': True,
                               'coords': coords})

    return title_boxes, text_boxes, image
