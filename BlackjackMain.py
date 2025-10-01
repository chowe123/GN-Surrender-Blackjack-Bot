import ReadVars
from PIL import ImageGrab
import cv2
import numpy as np
import time
import pyautogui
import keyboard
import pandas as pd
import OCR
import ButtonChecker
import boundingbox
import numpy as np
import resource_path
import random

dealer = ()
playerTable = ()
buttonBbox = ()



strategy_sheet = r"Strategy.xlsx"
strategy_sheet = resource_path.resource_path(strategy_sheet)

split = pd.read_excel(strategy_sheet, sheet_name="Split")
split.columns = split.columns.map(str)
split[split.columns[0]] = split[split.columns[0]].astype("string")
surrender = pd.read_excel(strategy_sheet, sheet_name="Surrender")
surrender.columns = surrender.columns.map(str)
surrender[surrender.columns[0]] = surrender[surrender.columns[0]].astype("string")
soft = pd.read_excel(strategy_sheet, sheet_name="Soft Totals")
soft.columns = soft.columns.map(str)
soft[soft.columns[0]] = soft[soft.columns[0]].astype(str)
hard = pd.read_excel(strategy_sheet, sheet_name="Hard Totals")
hard.columns = hard.columns.map(str)
hard[hard.columns[0]] = hard[hard.columns[0]].astype(str)

running = False  # toggle state
bets_placed = 0
last_print = None  # store last printed message
start_time = None  # track start time

def buttonClicker(location, bbox):
    abs_top_left = (location[0][0] + bbox[0], location[0][1] + bbox[1])
    abs_bottom_right = (location[1][0] + bbox[0], location[1][1] + bbox[1])

    midPoint = ((abs_top_left[0] + abs_bottom_right[0]) / 2,
                (abs_top_left[1] + abs_bottom_right[1]) / 2)

    pyautogui.moveTo(midPoint[0], midPoint[1])
    pyautogui.click()
    time.sleep(0.2)

def toggle_running():
    global running, bets_placed, start_time
    running = not running
    print("Script running:", running)
    if running and start_time is None:
        start_time = time.time()  # first time starting
    if not running and start_time is not None:
        elapsed = time.time() - start_time
        hours = elapsed / 3600
        hands_per_hour = bets_placed / hours if hours > 0 else 0
        print(f"Bets placed so far: {bets_placed}")
        print(f"Elapsed time: {elapsed/60:.2f} minutes")
        print(f"Hands/hour: {hands_per_hour:.2f}")

def main():
    global dealer, playerTable, buttonBbox
    variables = ReadVars.read_tuples_from_file("Vars.txt")
    dealer = variables.get("dealer", dealer)
    playerTable = variables.get("playerTable", playerTable)
    buttonBbox = variables.get("buttonBbox", buttonBbox)
    dynamic_dealer = variables.get("dynamicDealer", (1))[0]
    print(dealer, playerTable, buttonBbox)
    keyboard.add_hotkey("F8", toggle_running)
    print("Press F8 to start/stop script. Press ESC to exit.")
    attempted_unavailale_surrender = False
    while True:
        if not running:
            time.sleep(0.1)
            if keyboard.is_pressed("esc"):
                print("Exiting script.")
                break
            continue
        
        # Emergency stop
        if keyboard.is_pressed("esc"):
            print("Exiting script.")
            break

        time.sleep(0.5)
        

        
        buttons = ButtonChecker.check_buttons(bbox=buttonBbox)

        # --- Rebet Logic ---
        if "RebetDealAvailable.PNG" in buttons:
            attempted_unavailale_surrender = False
            global bets_placed, last_print
            if last_print != "Rebet Deal button detected.":
                bets_placed += 1
            print("Rebet Deal button detected.")
            last_print = "Rebet Deal button detected."
            buttonClicker(buttons["RebetDealAvailable.PNG"], bbox=buttonBbox)
            continue
        elif "RebetDealUnavailable.PNG" in buttons:
            attempted_unavailale_surrender = False
            print("Wait to click rebet.")
            last_print = "Wait to click rebet."
            continue
        else:
            try:
                playerLoc = OCR.find_player.detect_gold_boxes(bbox=playerTable)[0][0]
            except:
                continue

            player_text = str(OCR.ocr_card(OCR.find_player.detect_gold_boxes(bbox=playerTable)[0][0], mode='player'))
            if dynamic_dealer == (1):
                print("dynamic dealer bbox")
                dealer_text = str(OCR.ocr_card(OCR.find_player.detect_gold_boxes(bbox=dealer, lower_color=np.array([0, 0, 0]), upper_color=np.array([0, 0, 0]))[0][0], mode='dealer'))
            elif dynamic_dealer == (0):
                print("static dealer bbox")
                dealer_text = str(OCR.ocr_card(dealer, mode='dealer'))
            msg = f"Player: {player_text}, Dealer: {dealer_text}"
            print(msg)
            last_print = msg
            buttons = ButtonChecker.check_buttons(bbox=buttonBbox)

            DoubleAvailable = "DoubleAvailable.PNG" in buttons

            # --- Split Logic ---
            if "SplitAvailable.PNG" in buttons:
                splitAction = split.loc[split["Hand"] == player_text, dealer_text].values[0]
                if splitAction:
                    print("Splitting")
                    if "SplitAvailable.PNG" not in buttons:
                        continue
                    bets_placed += 1
                    buttonClicker(buttons["SplitAvailable.PNG"],bbox=buttonBbox)
                    last_print = "Splitting"
                    continue

            # --- Surrender Logic ---
            if "_" not in player_text and ("SurrenderAvailable.PNG" in buttons or "SurrenderUnavailable.PNG" in buttons):
                surrenderAction = surrender.loc[surrender["Hand"] == player_text, dealer_text].values[0]
                if surrenderAction and "SurrenderAvailable.PNG" in buttons:
                    print("Surrender button detected, surrendering")
                    last_print = "Surrendering"
                    if "SurrenderAvailable.PNG" not in buttons:
                        continue
                    buttonClicker(buttons["SurrenderAvailable.PNG"],bbox=buttonBbox)
                    continue
                elif surrenderAction and "SurrenderUnavailable.PNG" in buttons and not attempted_unavailale_surrender:
                    print("Surrender button not detected, trying anyways")
                    last_print = "Surrender button not detected, trying anyways"
                    if "SurrenderUnavailable.PNG" not in buttons:
                        continue
                    buttonClicker(buttons["SurrenderUnavailable.PNG"],bbox=buttonBbox)
                    attempted_unavailale_surrender = True
                    continue

            # --- Soft Hands Logic ---
            if "_" in player_text:
                print("In soft action")
                last_print = "In soft action"
                softAction = soft.loc[soft["Hand"] == player_text, dealer_text].values[0]
                if softAction == "D":
                    if DoubleAvailable:
                        print("Doubling Down")
                        if "DoubleAvailable.PNG" not in buttons:
                            print("Hitting instead")
                            last_print = "Hitting instead"
                            continue
                        bets_placed += 1
                        buttonClicker(buttons["DoubleAvailable.PNG"],bbox=buttonBbox)
                        last_print = "Doubling Down"
                        continue
                    else:
                        print("Hitting, cannot double")
                        last_print = "Hitting, cannot double"
                        if "HitAvailable.PNG" not in buttons:
                            continue
                        buttonClicker(buttons["HitAvailable.PNG"],bbox=buttonBbox)
                        continue
                if softAction == "Ds":
                    if DoubleAvailable:
                        print("Doubling Down")
                        if "DoubleAvailable.PNG" not in buttons:
                            continue
                        bets_placed += 1
                        buttonClicker(buttons["DoubleAvailable.PNG"],bbox=buttonBbox)
                        last_print = "Doubling Down"
                        continue
                    else:
                        print("Standing, cannot double")
                        last_print = "Standing, cannot double"
                        if "StandAvailable.PNG" not in buttons:
                            continue
                        buttonClicker(buttons["StandAvailable.PNG"],bbox=buttonBbox)
                        continue
                if softAction == "H":
                    print("Hitting")
                    last_print = "Hitting"
                    if "HitAvailable.PNG" not in buttons:
                        continue
                    buttonClicker(buttons["HitAvailable.PNG"],bbox=buttonBbox)
                    continue
                if softAction == "S":
                    print("Standing")
                    last_print = "Standing"
                    if "StandAvailable.PNG" not in buttons:
                        continue
                    buttonClicker(buttons["StandAvailable.PNG"],bbox=buttonBbox)
                    continue

            # --- Hard Hands Logic ---
            else:
                hardAction = hard.loc[hard["Hand"] == player_text, dealer_text].values[0]
                if hardAction == "D":
                    if DoubleAvailable:
                        print("Doubling Down")
                        bets_placed += 1
                        buttonClicker(buttons["DoubleAvailable.PNG"],bbox=buttonBbox)
                        last_print = "Doubling Down"
                        continue
                    else:
                        print("Hitting, cannot double")
                        last_print = "Hitting, cannot double"
                        if "HitAvailable.PNG" not in buttons:
                            continue
                        buttonClicker(buttons["HitAvailable.PNG"],bbox=buttonBbox)
                        continue
                if hardAction == "H":
                    print("Hitting")
                    last_print = "Hitting"
                    if "HitAvailable.PNG" not in buttons:
                        continue
                    buttonClicker(buttons["HitAvailable.PNG"],bbox=buttonBbox)
                    continue
                if hardAction == "S":
                    print("Standing")
                    last_print = "Standing"
                    if "StandAvailable.PNG" not in buttons:
                        continue
                    buttonClicker(buttons["StandAvailable.PNG"],bbox=buttonBbox)
                    continue


if __name__ == "__main__":
    main()
    
