import cv2
import numpy as np
import pyautogui

def pick_bbox():

    screenshot = pyautogui.screenshot()
    
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    clone = img.copy()

    bbox = []
    drawing = False
    start_point = (-1, -1)

    def draw_rectangle(event, x, y, flags, param):
        nonlocal drawing, start_point, bbox, img
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            img = clone.copy()
            cv2.rectangle(img, start_point, (x, y), (0, 255, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            bbox = [start_point[0], start_point[1], x, y]
            cv2.rectangle(img, start_point, (x, y), (0, 255, 0), 2)

    cv2.namedWindow("Select BBox (drag with mouse)")
    cv2.setMouseCallback("Select BBox (drag with mouse)", draw_rectangle)

    while True:
        cv2.imshow("Select BBox (drag with mouse)", img)
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # ENTER to confirm
            break
        elif key == 27:  # ESC to cancel
            bbox = []
            break

    cv2.destroyAllWindows()

    if bbox:
        # Ensure bbox is (left, top, right, bottom)
        x1, y1, x2, y2 = bbox
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        cropped = clone[y1:y2, x1:x2]

        # Show only cropped region
        cv2.imshow("Selected Region", cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return (x1, y1, x2, y2)
    else:
        return None

    
if __name__ == "__main__":
    bbox = pick_bbox()
    if bbox:
        print("Bounding box:", bbox)
        # Example: (100, 200, 400, 300)
    else:
        print("No box selected.")
