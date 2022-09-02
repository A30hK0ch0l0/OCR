from lfocr.box_utils_conditions import *


def merge_boxes(responses, config, box_type):
    old_boxes_flag = len(responses) * [True]
    new_boxes = []
    for outer_idx, outer_text in enumerate(responses):

        if old_boxes_flag[outer_idx]:
            old_boxes_flag[outer_idx] = False
            # if outer_text['title']:
            new_box = []
            new_x0 = outer_text['x']
            new_y0 = outer_text['y']
            new_x1 = outer_text['x'] + outer_text['w']
            new_y1 = outer_text['y'] + outer_text['h']
            new_box.append(outer_text)
            old_boxes_flag[outer_idx] = False

            # for inner_idx, inner_text in enumerate(responses):
            inner_idx = 0
            while inner_idx < len(responses):
                inner_text = responses[inner_idx]
                # print(inner_idx)
                if old_boxes_flag[inner_idx] and (
                        (box_type == 'text' and eval(
                            'merge_text_conditions(new_x0, new_y0, new_x1, new_y1, inner_text, config)')) or
                        (box_type == 'title' and eval(
                            'merge_title_conditions(new_x0, new_y0, new_x1, new_y1, inner_text, config)')) or
                        (box_type == 'news' and eval(
                            'merge_text_boxes_of_one_news_conditions(new_x0, new_y0, new_x1, new_y1, inner_text, config)'))

                ):
                    new_x0 = min(new_x0, inner_text['x'])
                    new_y0 = min(new_y0, inner_text['y'])
                    new_x1 = max(new_x1, inner_text['x'] + inner_text['w'])
                    new_y1 = max(new_y1, inner_text['y'] + inner_text['h'])
                    new_box.append(inner_text)
                    old_boxes_flag[inner_idx] = False

                    inner_idx = -1
                    continue
                else:
                    pass
                # print("not merged")
                inner_idx += 1
            new_boxes.append([new_box, new_x0, new_y0, new_x1, new_y1])

    return new_boxes


def set_box_new_coordinates(text_boxes, config, initial_idx, box_type):
    merged_response = []
    line_count = -1
    text = ''
    for box_idx, box in enumerate(text_boxes):
        if box_type == 'text':
            line_count = calc_text_box_lines(box, config)
        if box_type == 'news':
            text = merge_news_text(box, config)
            if text == '':
                continue

        x = box[1]
        y = box[2]
        w = box[3] - box[1]
        h = box[4] - box[2]

        coords = "{},{},{},{}".format(x, y, x + w, y + h)
        merged_response.append({'text': text, 'x': x, 'y': y, 'w': w, 'h': h, 'coords': coords,
                                'idx': initial_idx + box_idx, 'title': box_type == 'title', 'vis': True,
                                'lines_count': line_count
                                })

    return merged_response, len(merged_response)


def merge_news_text(box, config):
    sorted_box = sorted(box[0], key=lambda k: k['x'] + k['w'], reverse=True)

    text = '\n'.join([t['text'] for t in sorted_box])
    return text


def calc_text_box_lines(box, config):
    sorted_box = sorted(box[0], key=lambda k: k['y'])
    heights = [t['h'] for t in sorted_box]

    mean = np.mean(heights)
    std = np.std(heights) + config['std_range']
    refined_box = 0
    for _, h in enumerate(heights):
        if abs(h - mean) > std:
            refined_box += int(np.ceil(h / mean))
        else:
            refined_box += 1
    #     pass
    for temp_idx in range(len(sorted_box) - 1):
        box1_y0 = sorted_box[temp_idx]['y']
        box1_y1 = sorted_box[temp_idx]['y'] + sorted_box[temp_idx]['h']

        box2_y0 = sorted_box[temp_idx + 1]['y']
        box2_y1 = sorted_box[temp_idx + 1]['y'] + sorted_box[temp_idx + 1]['h']
        if len(np.intersect1d(list(range(box1_y0, box1_y1)), list(range(box2_y0, box2_y1)))) > config[
            'merge_text_limit_intersect']:
            refined_box -= 1

    return refined_box


def match_titles_and_texts(title_boxes, text_boxes):
    title_and_text_pairs = []
    texts_flag = len(text_boxes) * [True]
    titles_flag = len(title_boxes) * [True]
    for selected_title_idx, selected_title_box in enumerate(title_boxes):

        is_overlap = False
        xmin_1, ymin_1, xmax_1, ymax_1 = map(int, selected_title_box['coords'].split(','))
        center_x_title = (xmax_1 + xmin_1) / 2
        for selected_text_idx, selected_text_box in enumerate(text_boxes):
            xmin_2, ymin_2, xmax_2, ymax_2 = map(int, selected_text_box['coords'].split(','))
            if is_overlapping(xmin_1, ymin_1, xmax_1, ymax_1, xmin_2, ymin_2, xmax_2, ymax_2):
                is_overlap = True
                texts_flag[selected_text_idx] = False
                title_and_text_pairs.append([selected_title_box, selected_text_box])
                titles_flag[selected_title_idx] = False
                texts_flag[selected_text_idx] = False

        if not is_overlap:
            find_title_box = False
            min_text_box_distance = 1000000000
            find_text_idx = -1
            for selected_text_idx, selected_text_box in enumerate(text_boxes):
                xmin, ymin, xmax, _ = map(int, selected_text_box['coords'].split(','))
                # texts_flag[selected_text_idx] and
                if ymax_1 < ymin and is_under(center_x_title, xmin, xmax) and (ymin - ymax_1) < min_text_box_distance:
                    find_text_idx = selected_text_idx
                    min_text_box_distance = ymin - ymax_1

            for compared_title_idx, compared_title_box in enumerate(title_boxes):
                xmin, ymin, xmax, _ = map(int, compared_title_box['coords'].split(','))
                if ymax_1 < ymin and is_under(center_x_title, xmin, xmax) and (ymin - ymax_1) < min_text_box_distance:
                    find_title_box = True

            if find_text_idx >= 0 and not find_title_box:
                title_and_text_pairs.append([selected_title_box, text_boxes[find_text_idx]])
                titles_flag[selected_title_idx] = False
                texts_flag[find_text_idx] = False

    final_result = []

    for pair in title_and_text_pairs:
        title = pair[0]['text']
        text = pair[1]['text']
        final_result.append({'title': title, 'text': text})

    for selected_title_idx, selected_title_box in enumerate(title_boxes):
        if titles_flag[selected_title_idx]:
            title = selected_title_box['text']
            text = ''
            final_result.append({'title': title, 'text': text})

    for selected_text_idx, selected_text_box in enumerate(text_boxes):
        if texts_flag[selected_text_idx]:
            title = ''
            text = selected_text_box['text']
            final_result.append({'title': title, 'text': text})

    return final_result


def new_version_matching(title_boxes, text_boxes, config):
    title_and_text_pairs = []
    texts_flag = [True for _ in range(len(text_boxes))]
    boxes_assign_to_titles = [[] for _ in title_boxes]
    thr = config['merge_limit_x_for_one_news']
    for selected_text_idx, selected_text_box in enumerate(text_boxes):

        xmin_text, ymin_text, xmax_text, ymax_text = map(int, selected_text_box['coords'].split(','))
        find_text_box = False
        min_text_box_distance = 1000000000
        find_title_idx = -1
        for selected_title_idx, selected_title_box in enumerate(title_boxes):
            xmin, ymin, xmax, ymax = map(int, selected_title_box['coords'].split(','))
            if ymin_text > ymax and is_intersect_on_x_axis(xmin_text, xmax_text, selected_title_box, 10) and (
                    ymin_text - ymax) < min_text_box_distance and (ymin_text - ymax) < 2000:
                find_title_idx = selected_title_idx
                min_text_box_distance = ymin_text - ymax

        for compared_text_idx, compared_text_box in enumerate(text_boxes):
            xmin, ymin, xmax, ymax = map(int, compared_text_box['coords'].split(','))
            if compared_text_idx != selected_text_idx and ymin_text > ymax and \
                    is_intersect_on_x_axis(xmin_text, xmax_text, compared_text_box, 10) and \
                    (ymin_text - ymax) < min_text_box_distance:
                find_text_box = True
                min_text_box_distance = ymin_text - ymax

        if find_title_idx >= 0 and not find_text_box:
            texts_flag[selected_text_idx] = False
            boxes_assign_to_titles[find_title_idx].append(selected_text_box)

    for title_idx, assigned_box in enumerate(boxes_assign_to_titles):
        assigned_box = sorted(assigned_box, key=lambda k: k['x'] + k['w'], reverse=True)
        if len(assigned_box) >= 1:
            boxes_assign_to_titles, texts_flag = merge_each_news_boxes(boxes_assign_to_titles, title_idx, text_boxes,
                                                                       texts_flag,
                                                                       assigned_box, thr)

    for title_idx, assigned_box in enumerate(boxes_assign_to_titles):
        if len(assigned_box) == 0:
            boxes_assign_to_titles, texts_flag = merge_each_news_boxes(boxes_assign_to_titles, title_idx, text_boxes,
                                                                       texts_flag,
                                                                       [title_boxes[title_idx]], thr, r=0, l=2.2)

    news_boxes = []
    title_news_pairs = []
    for title_idx, assigned_text_box in enumerate(boxes_assign_to_titles):
        sorted_box = sorted(assigned_text_box, key=lambda k: k['x'] + k['w'], reverse=True)
        text = '\n'.join([t['text'] for t in sorted_box])
        if len(assigned_text_box) == 0:
            title_news_pairs.append(
                {'title': title_boxes[title_idx]['text'], 'content': None,
                 'title_coords': coords_reformater(title_boxes[title_idx]['coords']),
                 'content_coords': None})
            continue

        x0, y0, x1, y1 = merge_cordinates(assigned_text_box)
        coords = "{},{},{},{}".format(x0, y0, x1, y1)
        news_boxes.append({'text': text, 'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0, 'coords': coords,
                           'idx': title_idx + 100, 'title': False == 'title', 'vis': True,
                           'lines_count': -13
                           })

        title_news_pairs.append(
            {'title': title_boxes[title_idx]['text'], 'content': text,
             'title_coords': coords_reformater(title_boxes[title_idx]['coords']),
             'content_coords': coords_reformater(coords)})

    for idx, text_box in enumerate(text_boxes):
        if texts_flag[idx]:
            title_news_pairs.append(
                {'title': None, 'content': text_box['text'], 'title_coords': None,
                 'content_coords': coords_reformater(text_box['coords'])})

    return news_boxes, title_news_pairs


def merge_each_news_boxes(boxes_assign_to_titles, title_idx, box, flag, assigned_box, thr, r=1.0, l=1.0):
    idx = 0
    x0, y0, x1, y1 = merge_cordinates(assigned_box)
    while idx < len(flag):
        if flag[idx]:

            temp_x0 = box[idx]['x']
            temp_y0 = box[idx]['y']
            temp_x1 = box[idx]['x'] + box[idx]['w']
            temp_y1 = box[idx]['y'] + box[idx]['h']

            distance_left = abs(x0 - temp_x1)
            distance_right = abs(x1 - temp_x0)
            if is_intersect_on_y(y0, y1, temp_y0, temp_y1, 10) and (
                    (distance_left < thr * l) or (distance_right < thr * r)):
                boxes_assign_to_titles[title_idx].append(box[idx])
                x0, y0, x1, y1 = merge_cordinates(boxes_assign_to_titles[title_idx])
                flag[idx] = False
                idx = -1
        idx += 1
    return boxes_assign_to_titles, flag


def is_intersect_on_y(new_y0, new_y1, y0, y1, threshold):
    if (len(np.intersect1d(list(range(new_y0, new_y1)),
                           list(range(y0,
                                      y1))))) > threshold:
        return True
    return False


def merge_cordinates(boxes):
    x0 = 1000000
    y0 = 1000000
    x1 = -1
    y1 = -1

    for box in boxes:
        x0 = min(x0, box['x'])
        y0 = min(y0, box['y'])
        x1 = max(x1, box['x'] + box['w'])
        y1 = max(y1, box['y'] + box['h'])

    return x0, y0, x1, y1


def calc_mean_distance(boxes):
    idx = 0
    distance = 0
    while idx < len(boxes) - 1:
        right_box_x0 = boxes[idx]['x']
        left_box_x1 = boxes[idx + 1]['x'] + boxes[idx + 1]['w']
        distance += (abs(right_box_x0 - left_box_x1))
        idx += 1
    mean_distance = distance // (len(boxes) - 1)
    return mean_distance


def merge_near_box_based_distance():
    pass


def remove_titles_based_on_len_thresholds(titles):
    refine_titles = []
    for title in titles:
        if len(title['text'].split(' ')) > 25 or title['text'].count('\n') > 4 or len(title['text']) < 3:
            continue
        refine_titles.append(title)

    return refine_titles


def remove_texts_based_on_len_thresholds(texts):
    refine_texts = []
    for text in texts:
        if len(text['text'].split(' ')) < 6 or text['text'].count('\n') < 2:
            # print(text)
            continue
        refine_texts.append(text)

    return refine_texts


def coords_reformater(coords):
    x0, y0, x1, y1 = coords.split(',')
    result = {
        "top_left": {
            "x": int(x0),
            "y": int(y0)
        },
        "bottom_right": {
            "x": int(x1),
            "y": int(y1)
        }
    }
    return result
