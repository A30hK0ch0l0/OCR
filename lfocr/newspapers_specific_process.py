def erase_area(pages, parts):
    refined_pages = []
    for idx, page in enumerate(pages):

        temp_page = page
        if idx in parts.keys() or idx - len(pages) in parts.keys():
            dict_idx = min(idx, idx - len(pages))
            for section in parts[dict_idx]:
                x0 = section[0]
                y0 = section[1]
                x1 = section[2]
                y1 = section[3]
                temp_page[y0:y1, x0:x1] = (255, 255, 255)

        refined_pages.append(temp_page)

    return refined_pages
