import cv2
import numpy as np
from PIL import ImageGrab
import os
import resource_path

# Path to your folder of images
image_folder = r"BJ Buttons"
image_folder = resource_path.resource_path(image_folder)

# Image pairs with their specific color ranges (lower, upper)
image_pairs = [
    ("SplitAvailable.PNG", "SplitUnavailable.PNG", np.array([28, 255, 223]), np.array([28, 255, 236])),
    ("DoubleAvailable.PNG", "DoubleUnavailable.PNG", np.array([45, 193, 245]), np.array([45, 194, 255])),
    ("SurrenderAvailable.PNG", "SurrenderUnavailable.PNG", np.array([0, 0, 242]), np.array([60, 5, 255]))
]

# Create dictionary: available_image -> (unavailable_image, lower_color, upper_color)
pair_dict = {pair[0]: (pair[1], pair[2], pair[3]) for pair in image_pairs}

# Screen bbox
def check_buttons(bbox):
    # Grab screen
    screenshot = ImageGrab.grab(bbox=bbox)
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def find_image_location(template_name, screen_img, threshold=0.5):
        """Returns top-left and bottom-right coordinates of the detected image, or None."""
        template_path = os.path.join(image_folder, template_name)
        template = cv2.imread(template_path)
        if template is None:
            print(f"Error: Could not load template {template_path}")
            return None

        # Rescale template if larger than screen region
        screen_h, screen_w = screen_img.shape[:2]
        templ_h, templ_w = template.shape[:2]
        if templ_h > screen_h or templ_w > screen_w:
            scale_h = screen_h / templ_h
            scale_w = screen_w / templ_w
            scale = min(scale_h, scale_w, 1.0)  # avoid upscaling
            new_w = int(templ_w * scale)
            new_h = int(templ_h * scale)
            template = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
            #print(f"Resized {template_name} to {new_w}x{new_h} to fit screen region.")

        result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            h, w = template.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            return top_left, bottom_right
        return None

    def is_color_in_region(img, top_left, bottom_right, lower_color, upper_color):
        """Checks if a given color exists in the detected region."""
        y1, y2 = top_left[1], bottom_right[1]
        x1, x2 = top_left[0], bottom_right[0]

        if y1 >= y2 or x1 >= x2:
            print("Warning: Invalid region coordinates!")
            return False

        region = img[y1:y2, x1:x2]

        if region.size == 0:
            print("Warning: Empty region!")
            return False

        # Convert region to HSV
        region_hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

        # Create mask using HSV color range
        mask = cv2.inRange(region_hsv, lower_color, upper_color)
        count = cv2.countNonZero(mask)
        #print count and lower/upper bounds for debugging
        #print(f"Color check in region: count={count}, lower={lower_color}, upper={upper_color}")
        return count > 0

    # Get all images in folder
    all_images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    detected_images = {}
    for key in pair_dict:
        if key in all_images:
            all_images.remove(key)
            all_images.remove(pair_dict[key][0])  # Remove unavailable version too
            detection = find_image_location(key, screen_img)
            if detection:
                if is_color_in_region(screen_img, detection[0], detection[1], pair_dict[key][1], pair_dict[key][2]):
                    detected_images[key] = detection
                else:
                    detected_images[pair_dict[key][0]] = detection

    for img in all_images:
        detection = find_image_location(img, screen_img)
        if detection:
            detected_images[img] = detection

    return detected_images

if __name__ == "__main__":
    detected = check_buttons(bbox=(692,896,1170,1001))
    print("Detected images:", detected)