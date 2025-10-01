# BlackjackGUI.py
import tkinter as tk
import BlackjackMain   # contains main()
import ReadVars        # contains read_tuples_from_file, update_var_in_file, setBBox functions
import NumberGrabber   # contains NumberGrabberTest function
import OCR            # contains ocr_card function
import find_player
import numpy as np

from os import path
path_to_dat = path.abspath(path.join(path.dirname(__file__)))



def run_main():
    """Run BlackjackMain.main() directly on the main thread."""
    BlackjackMain.main()  # Run directly, no threading

def update_dealer():
    ReadVars.setDealerBbox()

def update_player_table():
    ReadVars.setPlayerTableBbox()

def update_button_bbox():
    ReadVars.setButtonBbox()

def refresh_vars():
    """Refresh and show current variable values from Vars.txt."""
    vars_dict = ReadVars.read_tuples_from_file("Vars.txt")
    dealer_label.config(text=f"Dealer: {vars_dict.get('dealer')}")
    player_label.config(text=f"Player Table: {vars_dict.get('playerTable')}")
    button_label.config(text=f"Button: {vars_dict.get('buttonBbox')}")
    
def run_NumberGrabber():
    vars_dict = ReadVars.read_tuples_from_file("Vars.txt")
    NumberGrabber.NumberGrabberTest(
        playerTableBbox=vars_dict.get("playerTable"),
        DealerBbox=vars_dict.get("dealer")
    )
    
def run_OCR_Test():
    vars_dict = ReadVars.read_tuples_from_file("Vars.txt")
    player_text = OCR.ocr_card(find_player.detect_gold_boxes(bbox=vars_dict.get('playerTable'))[0][0],
                               'player', show_images=False)
    
    if vars_dict.get('dynamicDealer', (1))[0] == 0:
        print("OCR Test, static dealer bbox")
        dealer_text = OCR.ocr_card(
            vars_dict.get('dealer'), 
            'dealer',
            show_images=False
        )
    if vars_dict.get('dynamicDealer', (1))[0] == 1:
        print("OCR Test, dynamic dealer bbox")
        dealer_text = OCR.ocr_card(
            find_player.detect_gold_boxes(bbox=vars_dict.get('dealer'), lower_color=np.array([0, 0, 0]), upper_color=np.array([0, 0, 0]))[0][0], 
            'dealer',
            show_images=False
        )
    print(vars_dict.get('dynamicDealer')[0])
    print(f"Player OCR: {player_text}")
    print(f"Dealer OCR: {dealer_text}")
    
# --- Tkinter GUI setup ---
root = tk.Tk()
root.title("Blackjack Controller")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Run main button
run_button = tk.Button(frame, text="Run Blackjack Main", command=run_main, width=25, height=2)
run_button.pack(pady=5)

# Update bbox buttons
dealer_button = tk.Button(frame, text="Set Dealer BBox", command=lambda:[update_dealer(), refresh_vars()], width=25)
dealer_button.pack(pady=5)

player_button = tk.Button(frame, text="Set Player Table BBox", command=lambda:[update_player_table(), refresh_vars()], width=25)
player_button.pack(pady=5)

button_bbox_button = tk.Button(frame, text="Set Button BBox", command=lambda:[update_button_bbox(), refresh_vars()], width=25)
button_bbox_button.pack(pady=5)

# Labels showing current values
dealer_label = tk.Label(frame, text="Dealer: ")
dealer_label.pack()
player_label = tk.Label(frame, text="Player Table: ")
player_label.pack()
button_label = tk.Label(frame, text="Button: ")
button_label.pack()

# NumberGrabber test button
number_grabber_button = tk.Button(frame, text="Run NumberGrabber", command=run_NumberGrabber, width=25, height=2)
number_grabber_button.pack(pady=5)
# OCR test button
ocr_test_button = tk.Button(frame, text="Run OCR Test", command=run_OCR_Test, width=25, height=2)
ocr_test_button.pack(pady=5)


# Instruction note for hotkeys
note_label = tk.Label(frame, text="Press F8 to start/stop script. Press ESC to exit.", fg="blue")
note_label.pack(pady=10)

# Refresh on start
refresh_vars()

root.mainloop()
