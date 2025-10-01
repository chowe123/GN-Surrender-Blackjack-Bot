
from PIL import Image, ImageGrab
import cv2
import numpy as np
import find_player
import os

import resource_path


#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

dealer = (983, 310, 1010, 330)

valid_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 
                '1/11', '2/12', '3/13', '4/14', '5/15', '6/16', '7/17', '8/18', '9/19', '10/20']

# Create separate folders for player and dealer images
PLAYER_DIR = "captured_cards/player"
DEALER_DIR = "captured_cards/dealer"

PLAYER_DIR = resource_path.resource_path(PLAYER_DIR)
DEALER_DIR = resource_path.resource_path(DEALER_DIR)
os.makedirs(PLAYER_DIR, exist_ok=True)
os.makedirs(DEALER_DIR, exist_ok=True)

def ocr_card(bbox=(125, 439, 1777, 847), mode='player'):
    # Grab screenshot as PIL Image
    screen_shot = ImageGrab.grab(bbox=bbox)
    img_rgb = np.array(screen_shot)  # Already in RGB order
    
    # Upscale using OpenCV (colors remain correct in RGB array)
    height, width = img_rgb.shape[:2]
    scale = 5
    processed = cv2.resize(img_rgb, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC)
    
    # Prompt user for label
    label = input(f"Enter label for this {mode} card: ").strip()
    
    # Select folder based on mode
    save_dir = PLAYER_DIR if mode == 'player' else DEALER_DIR
    filename = f"{label}.png"
    filepath = os.path.join(save_dir, filename)
    
    # Save using PIL (true RGB)
    Image.fromarray(processed).save(filepath)
    print(f"Saved image as {filepath}")
    
    # # OCR
    # text = pytesseract.image_to_string(
    #     processed, 
    #     config='--psm 7 -c tessedit_char_whitelist=0123456789/ --user-words tessdata/user-words.txt'
    # )
    
    # if text.strip() == '1':
    #     return '7'
    # return text.strip()
    
def NumberGrabberTest(playerTableBbox, DealerBbox):
    player_box = find_player.detect_gold_boxes(bbox=playerTableBbox)[0][0]
    player_text = ocr_card(player_box, mode='player')
    dealer_box = DealerBbox
    dealer_text = ocr_card(dealer_box, mode='dealer')
    

if __name__ == "__main__":
    player_box = find_player.detect_gold_boxes()[0][0]
    player_text = ocr_card(player_box, mode='player')
    dealer_text = ocr_card(find_player.detect_gold_boxes(bbox=(945, 297, 1054, 345), lower_color=np.array([0, 0, 0]), upper_color=np.array([0, 0, 0]))[0][0], mode='dealer')

    print(f"Player OCR: {player_text}")
    print(f"Dealer OCR: {dealer_text}")
