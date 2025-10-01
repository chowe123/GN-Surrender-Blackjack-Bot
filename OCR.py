from PIL import Image, ImageGrab
import cv2
import numpy as np
import find_player
from skimage.metrics import structural_similarity as ssim
import os

import resource_path

dealer = (983, 310, 1010, 330)

PLAYER_DIR = "captured_cards/player"
DEALER_DIR = "captured_cards/dealer"

PLAYER_DIR = resource_path.resource_path(PLAYER_DIR)
DEALER_DIR = resource_path.resource_path(DEALER_DIR)

def ocr_card(bbox, mode, resize_dim=(100,100), show_images=False):
    # Grab screenshot and convert to BGR for OpenCV
    screen_shot = ImageGrab.grab(bbox=bbox)
    img = np.array(screen_shot)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img_resized = cv2.resize(img_rgb, resize_dim, interpolation=cv2.INTER_CUBIC)
    
    folder = PLAYER_DIR if mode == 'player' else DEALER_DIR
    best_score = -1
    best_match_label = None
    
    for file in os.listdir(folder):
        if not file.lower().endswith(".png"):
            continue
        
        card_img = np.array(Image.open(os.path.join(folder, file)))
        card_bgr = cv2.cvtColor(card_img, cv2.COLOR_RGB2BGR)
        card_resized = cv2.resize(card_bgr, resize_dim, interpolation=cv2.INTER_CUBIC)
        
        # Compute SSIM in RGB
        score = ssim(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB),
                     cv2.cvtColor(card_resized, cv2.COLOR_BGR2RGB),
                     channel_axis=-1)
        
        # Print similarity score to console
        
        
        if show_images:
            print(f"Comparing with {file}: SSIM = {score:.4f}")
            combined = np.hstack((img_resized, card_resized))
            cv2.putText(combined, f"SSIM: {score:.3f}", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow(f"Comparing {file}", combined)
            cv2.waitKey(500)
            cv2.destroyAllWindows()
        
        if score > best_score:
            best_score = score
            best_match_label = os.path.splitext(file)[0]
    
    return best_match_label

    

if __name__ == "__main__":
    print(find_player.detect_gold_boxes(bbox=(16, 487, 1811, 866))[0][0])
    player_text = ocr_card(bbox=find_player.detect_gold_boxes(bbox=(16, 487, 1811, 866))[0][0], mode='player', show_images=True)
    dealer_text = ocr_card(
        bbox=(979,304,1015,334), 
        mode='dealer',
        show_images=False
    )

    print(f"Player OCR: {player_text}")
    print(f"Dealer OCR: {dealer_text}")
