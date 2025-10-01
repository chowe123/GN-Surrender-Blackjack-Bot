import cv2
import numpy as np
from PIL import ImageGrab

def get_hsv_range_from_bbox(screenshot_bbox, min_value=0):
    # Take screenshot
    screenshot = ImageGrab.grab(bbox=screenshot_bbox)
    img_np = np.array(screenshot)
    img = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    # Variables for drawing
    drawing = False
    ix, iy = -1, -1
    rect = None

    def draw_rectangle(event, x, y, flags, param):
        nonlocal ix, iy, drawing, rect, img_display
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                img_display = img.copy()
                cv2.rectangle(img_display, (ix, iy), (x, y), (0, 255, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            rect = (min(ix, x), min(iy, y), max(ix, x), max(iy, y))
            cv2.rectangle(img_display, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)

    img_display = img.copy()
    cv2.namedWindow("Draw Rectangle")
    cv2.setMouseCallback("Draw Rectangle", draw_rectangle)

    while True:
        cv2.imshow("Draw Rectangle", img_display)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC to exit
            cv2.destroyAllWindows()
            return None
        elif rect is not None and key == 13:  # ENTER to confirm selection
            break

    x1, y1, x2, y2 = rect
    roi = img[y1:y2, x1:x2]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Filter out very dark pixels (likely black)
    mask = hsv_roi[:, :, 2] > min_value
    filtered_pixels = hsv_roi[mask]

    if filtered_pixels.size == 0:
        print("No pixels above the min_value threshold in the selected area.")
        lower_hsv = np.array([0, 0, 0])
        upper_hsv = np.array([0, 0, 0])
    else:
        # Compute min/max HSV from filtered pixels
        h_min, s_min, v_min = np.min(filtered_pixels, axis=0)
        h_max, s_max, v_max = np.max(filtered_pixels, axis=0)
        lower_hsv = np.array([h_min, s_min, v_min])
        upper_hsv = np.array([h_max, s_max, v_max])

    cv2.destroyAllWindows()
    print(f"HSV Range -> Lower: {lower_hsv}, Upper: {upper_hsv}")
    
    return lower_hsv, upper_hsv

# Example usage:
bbox = (1314, 929, 1646, 961)
lower_hsv, upper_hsv = get_hsv_range_from_bbox(bbox)
