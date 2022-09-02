import cv2
import numpy as np


def remove_noise_and_smooth(img):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        img = cv2.bitwise_or(img, closing)

        return img
    except IOError:
        print("Error while reading the file.")


def remove_box_lines(image, config):
    # gray convertion
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)

    # threshold
    thresh_x = cv2.threshold(abs_grad_x, 0, 255, cv2.THRESH_OTSU)[1]
    thresh_y = cv2.threshold(abs_grad_y, 0, 255, cv2.THRESH_OTSU)[1]

    # bluring
    kernel_size = 3
    blur_thresh_x = cv2.GaussianBlur(thresh_x, (kernel_size, kernel_size), 0)
    blur_thresh_y = cv2.GaussianBlur(thresh_y, (kernel_size, kernel_size), 0)

    # Run Hough on edge detected image
    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = config['min_line_length']  # minimum number of pixels making up a line
    max_line_gap = config['max_line_gap']  # maximum gap in pixels between connectable line segments
    line_image = np.copy(gray) * 0  # creating a blank to draw lines on

    # Vertical lines
    vertical_lines = cv2.HoughLinesP(blur_thresh_x, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)

    if vertical_lines is not None:
        for line in vertical_lines:
            for x1, y1, x2, y2 in line:
                # here it's possible to add a selection of only vertical lines
                if np.abs(y1 - y2) > 0.1 * np.abs(x1 - x2):
                    cv2.line(line_image, (x1, y1), (x2, y2), 255, 5)
    # cv2.imwrite('1_line_image.jpg', line_image)

    horizontal_lines = cv2.HoughLinesP(blur_thresh_y, rho, theta, threshold, np.array([]), min_line_length,
                                       max_line_gap)

    if horizontal_lines is not None:
        for line in horizontal_lines:
            for x1, y1, x2, y2 in line:
                # here it's possible to add a selection of only horizontal lines
                if np.abs(x1 - x2) > 0.1 * np.abs(y1 - y2):
                    cv2.line(line_image, (x1, y1), (x2, y2), 255, 5)

    # cv2.imwrite('2_line_image_horizontal.jpg', line_image)

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # remove lines
    clean_thresh = cv2.subtract(thresh, line_image)

    return clean_thresh


def remove_article_box_lines(bw, config):
    horizontal = np.copy(bw)
    vertical = np.copy(bw)

    # Specify size on horizontal axis
    cols = horizontal.shape[1]
    horizontal_size = cols // config['horizontal_size']
    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)
    # Show extracted horizontal lines
    # show_wait_destroy("horizontal", cv.resize(horizontal, (512, 512)))
    # [horiz]
    # [vert]
    # Specify size on vertical axis
    rows = vertical.shape[0]
    vertical_size = rows // config['vertical_size']
    # Create structure element for extracting vertical lines through morphology operations
    vertical_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
    # Apply morphology operations
    vertical = cv2.erode(vertical, vertical_structure)
    vertical = cv2.dilate(vertical, vertical_structure)

    vv = vertical.copy()
    xx = cv2.subtract((cv2.subtract(bw, vv)), horizontal)

    return xx


def find_phrase(clean_thresh, config):
    element = np.array(np.ones((config['element_array_row'], config['element_array_col'])))
    dilatation_thresh = cv2.dilate(clean_thresh, element)

    # cv2.imwrite('4_dilatation_thresh.jpg', dilatation_thresh)

    # Fill
    filled_thresh = dilatation_thresh.copy()
    contours, hierarchy = cv2.findContours(dilatation_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        cv2.drawContours(filled_thresh, [cnt], -1, 255, cv2.FILLED)

    # cv2.imwrite('5_filled_tresh.jpg', filled_thresh)

    # Draw bounding boxes
    bounding_box1 = filled_thresh.copy()
    contours, hierarchy = cv2.findContours(bounding_box1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(bounding_box1, (x, y), (x + w, y + h), 255, cv2.FILLED)

    # cv2.imwrite('6_bounding_box1.jpg', bounding_box1)

    return bounding_box1
