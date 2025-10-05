from PIL import ImageGrab
import cv2
import numpy as np
import pyautogui

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import os

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import os

def detect_boxes(bbox=(123, 449, 1777, 857), mode='player', min_area=400, tolerance=15):
    
    if mode == 'player':
        lower_color = np.array([20, 161, 54])  # Example lower HSV for gold
        upper_color = np.array([21, 206, 245])  # Example upper HSV for gold
    elif mode == 'dealer':
        lower_color = np.array([0, 0, 0])  # Example lower HSV for black
        upper_color = np.array([0, 0, 0])  # Example upper HSV for black
    screenshot = ImageGrab.grab(bbox=bbox)
    img_np = np.array(screenshot)
    img = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, lower_color, upper_color)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        if abs(w - h) <= tolerance:
            # Convert to screen coordinates
            screen_x1 = x + bbox[0]
            screen_y1 = y + bbox[1]
            screen_x2 = x + w + bbox[0]
            screen_y2 = y + h + bbox[1]
            boxes.append((screen_x1, screen_y1, screen_x2, screen_y2))

    return boxes, img








if __name__ == "__main__":
    import ReadVars
    varDict = ReadVars.read_tuples_from_file("Vars.txt")
    # Example usage
    table_bbox = varDict.get('playerTable', (123, 449, 1777, 857))
    lower_color = np.array([0, 0, 0])
    upper_color = np.array([0, 0, 0])

    detected_boxes, screenshot_img = detect_boxes(varDict['playerTable'], mode='player')
    print(detected_boxes)  # e.g., [(982, 309, 1012, 329), ...]

    # Draw boxes on the cropped image (convert back to relative coordinates)
    for x1, y1, x2, y2 in detected_boxes:
        rel_x1 = x1 - table_bbox[0]
        rel_y1 = y1 - table_bbox[1]
        rel_x2 = x2 - table_bbox[0]
        rel_y2 = y2 - table_bbox[1]
        cv2.rectangle(screenshot_img, (rel_x1, rel_y1), (rel_x2, rel_y2), (0, 255, 0), 2)

    # Show the image with detected boxes
    cv2.imshow("Detected Gold Boxes", screenshot_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    


