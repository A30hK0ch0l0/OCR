import numpy as np

"""
this is for when two box on same line but for some reason they are do not detected as a box
"""


def is_intersect_on_x_axis(new_x0, new_x1, inner_text, threshold):
    if (len(np.intersect1d(list(range(new_x0, new_x1)),
                           list(range(inner_text['x'],
                                      inner_text['x'] + inner_text['w']))))) > threshold:
        return True
    return False


def is_intersect_on_y_axis(new_y0, new_y1, inner_text, threshold):
    if (len(np.intersect1d(list(range(new_y0, new_y1)),
                           list(range(inner_text['y'],
                                      inner_text['y'] + inner_text['h']))))) > threshold:
        return True
    return False


def is_eligible_for_merge_on_x_axis(new_x0, new_x1, inner_text, threshold):
    if abs(new_x0 - inner_text['x']) < threshold or abs(
            new_x1 - (inner_text['x'] + inner_text['w'])) < threshold:
        return True
    return False


def is_eligible_for_merge_on_y_axis(new_y0, new_y1, inner_text, threshold):
    if abs(new_y1 - inner_text['y']) < threshold or abs(new_y0 - (inner_text['y'] + inner_text['h'])) < threshold:
        return True
    return False


"""
some thing like this 2type boxes:

        ||||||||||||            ||||||||||||||||||||||||
        |    a     |            |          b           |     
        ||||||||||||            ||||||||||||||||||||||||
     ||||||||||||||||||             ||||||||||||||
     |       b        |             |      a     |       
     ||||||||||||||||||             ||||||||||||||
"""


def is_cover(new_x0, new_x1, inner_text):
    if ((new_x0 < inner_text['x']) and (new_x1 > inner_text['x'] + inner_text['w'])) \
            or ((new_x0 > inner_text['x']) and (new_x1 < inner_text['x'] + inner_text['w'])):
        return True
    return False


def merge_text_conditions(new_x0, new_y0, new_x1, new_y1, inner_text, config):
    if is_eligible_for_merge_on_y_axis(new_y0, new_y1, inner_text, config['merge_text_limit_y']) and \
            (is_eligible_for_merge_on_x_axis(new_x0, new_x1, inner_text, config['merge_text_limit_x']) or
             is_cover(new_x0, new_x1, inner_text) or
             is_intersect_on_x_axis(new_x0, new_x1, inner_text, config['merge_text_limit_intersect'])):
        return True
    return False


def merge_title_conditions(new_x0, new_y0, new_x1, new_y1, inner_text, config):
    if (is_eligible_for_merge_on_y_axis(new_y0, new_y1, inner_text, config['merge_title_limit_y']) or
        is_eligible_for_merge_on_y_axis(new_y1, new_y0, inner_text, config['merge_title_limit_y'])) and \
            (
                    is_eligible_for_merge_on_x_axis(new_x0, new_x0, inner_text, config['merge_title_limit_x']) or
                    is_eligible_for_merge_on_x_axis(new_x1, new_x1, inner_text, config['merge_title_limit_x']) or
                    is_cover(new_x0, new_x1, inner_text) or
                    is_intersect_on_x_axis(new_x0, new_x1, inner_text, config['merge_title_limit_intersect'])
            ):
        return True
    return False


def merge_text_boxes_of_one_news_conditions(new_x0, new_y0, new_x1, new_y1, inner_text, config):
    if is_eligible_for_merge_on_x_axis(new_x1, new_x0, inner_text, config['merge_limit_x_for_one_news']) and \
            is_intersect_on_y_axis(new_y0, new_y1, inner_text, config['merge_limit_intersect_for_one_news']):
        return True
    return False


def is_under(center_box, x_min, x_max):
    return x_min < center_box < x_max


def is_overlapping(xmin_1, ymin_1, xmax_1, ymax_1, xmin_2, ymin_2, xmax_2, ymax_2):
    is_overlapping_x = xmax_1 >= xmin_2 and xmax_2 >= xmin_1
    is_overlapping_y = ymax_1 >= ymin_2 and ymax_2 >= ymin_1
    is_overlap = is_overlapping_x and is_overlapping_y
    return is_overlap
