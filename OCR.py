from PIL import Image, ImageGrab
import cv2
import numpy as np
import find_player
from skimage.metrics import structural_similarity as ssim
import os
from paddleocr import PaddleOCR
import paddle


import resource_path

dealer = (983, 310, 1010, 330)

PLAYER_DIR = "captured_cards/player"
DEALER_DIR = "captured_cards/dealer"

PLAYER_DIR = resource_path.resource_path(PLAYER_DIR)
DEALER_DIR = resource_path.resource_path(DEALER_DIR)

def imageCheck():
    #get list of all images in PLAYER_DIR and DEALER_DIR
    player_images = [f for f in os.listdir(PLAYER_DIR) if f.lower().endswith(".png")]
    dealer_images = [f for f in os.listdir(DEALER_DIR) if f.lower().endswith(".png")]
    required_player_images = ["4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", 
                "2_12", "3_13", "4_14", "5_15", "6_16", "7_17", "8_18", "9_19", "10_20"]
    required_dealer_images = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "1_11"]
    missing_player = [img for img in required_player_images if f"{img}.png" not in player_images]
    missing_dealer = [img for img in required_dealer_images if f"{img}.png" not in dealer_images]
    return missing_player, missing_dealer

paddle_ocr_model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    device="gpu",
    enable_mkldnn=True
    )

valid_values = set(['2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','1/11','2/12','3/13','4/14','5/15','6/16','7/17','8/18','9/19','10/20'])
valid_specific_card = set(['K','Q','J','10','5','6','9','8','7'])

def ocr_card(bbox, scale_factor=2, mode='player'):
    screen_shot = ImageGrab.grab(bbox=bbox)
    img = np.array(screen_shot)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # Resize for better OCR accuracy
    height, width = img_rgb.shape[:2]
    img_resized = cv2.resize(img_rgb, (width * scale_factor, height * scale_factor), interpolation=cv2.INTER_CUBIC)
    result = paddle_ocr_model.predict(img_resized)
    ret = result[0]['rec_texts'][0].strip()
    if ret in valid_values:
        ret = ret.replace('/', '_')
        return ret
    else:
        print("ERROR: {}".format(ret))
        return None
    
    
def ocr_specific_card(bbox, scale_factor=3):
    screen_shot = ImageGrab.grab(bbox=bbox)
    img = np.array(screen_shot)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # Resize for better OCR accuracy
    height, width = img_rgb.shape[:2]
    img_resized = cv2.resize(img_rgb, (width * scale_factor, height * scale_factor), interpolation=cv2.INTER_CUBIC)
    result = paddle_ocr_model.predict(img_resized)
    ret = result[0]['rec_texts'][0].strip()
    if ret in valid_specific_card:
        # if ret is 'K', 'Q', or 'J', convert to '10'
        if ret in ['K', 'Q', 'J']:
            ret = '10'
        return ret
    else:
        print("ERROR, Specific Card not Valid: {}".format(ret))
        
def ocr_card_old(bbox, mode, resize_dim=(200,200), show_images=False, ssim_threshold=0.05):
    # Grab screenshot and convert to BGR for OpenCV
    screen_shot = ImageGrab.grab(bbox=bbox)
    img = np.array(screen_shot)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img_resized = cv2.resize(img_rgb, resize_dim, interpolation=cv2.INTER_CUBIC)
    
    folder = PLAYER_DIR if mode == 'player' else DEALER_DIR
    best_score = -1
    best_match_label = None
    second_best_score = -1
    second_best_label = None
    
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
        
        if show_images:
            print(f"Comparing with {file}: SSIM = {score:.4f}")
            combined = np.hstack((img_resized, card_resized))
            cv2.putText(combined, f"SSIM: {score:.3f}", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow(f"Comparing {file}", combined)
            cv2.waitKey(500)
            cv2.destroyAllWindows()
        
        # Track best and second best
        if score > best_score:
            second_best_score, second_best_label = best_score, best_match_label
            best_score, best_match_label = score, os.path.splitext(file)[0]
        elif score > second_best_score:
            second_best_score, second_best_label = score, os.path.splitext(file)[0]
    
    # --- Tie-breaker check ---
    if second_best_label and abs(best_score - second_best_score) < ssim_threshold:
        print(f"SSIM too close: {best_match_label} ({best_score:.4f}) vs {second_best_label} ({second_best_score:.4f})")
        print("Running template matching as tie-breaker...")
        
        best_match_score = -1
        best_label_final = best_match_label
        for candidate_label in [best_match_label, second_best_label]:
            candidate_img = cv2.imread(os.path.join(folder, f"{candidate_label}.png"))
            candidate_resized = cv2.resize(candidate_img, resize_dim, interpolation=cv2.INTER_CUBIC)
            
            result = cv2.matchTemplate(img_resized, candidate_resized, cv2.TM_CCOEFF_NORMED)
            _, match_score, _, _ = cv2.minMaxLoc(result)
            print(f"Template match score for {candidate_label}: {match_score:.4f}")
            if show_images:
                print(f"Template match {candidate_label}: {match_score:.4f}")
                combined = np.hstack((img_resized, candidate_resized))
                cv2.putText(combined, f"T-Score: {match_score:.3f}", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.imshow(f"Tie-break {candidate_label}", combined)
                cv2.waitKey(500)
                cv2.destroyAllWindows()
            
            if match_score > best_match_score:
                
                best_match_score = match_score
                best_label_final = candidate_label
        
        return best_label_final
    
    return best_match_label









    

if __name__ == "__main__":
    import ReadVars
    vars_dict = ReadVars.read_tuples_from_file("Vars.txt")
    # player_text = ocr_card(bbox=find_player.detect_gold_boxes(bbox=vars_dict['playerTable'], white_crop=False)[0][0], mode='player', show_images=True)
    # print('Dealer OCR started')
    # dealer_text = ocr_card(
    #         find_player.detect_gold_boxes(bbox=vars_dict.get('dealer'), lower_color=np.array([0, 0, 0]), upper_color=np.array([0, 0, 0]))[0][0], 
    #         'dealer',
    #         show_images=True
    #     )
    
    player_text = ocr_card(find_player.detect_boxes(bbox=vars_dict['playerTable'], mode='player')[0][0], scale_factor=2)
    print(f"Player OCR: {player_text}")
    dealer_text = ocr_card(find_player.detect_boxes(bbox=vars_dict['dealer'], mode='dealer')[0][0], scale_factor=2)
    print(f"Dealer OCR: {dealer_text}")
    
    print(f"Specific Cards OCR Test: {ocr_specific_card((899, 689, 914, 716))}")
    
