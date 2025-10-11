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
import os

dealer = ()
playerTable = ()
buttonBbox = ()
valid_dealer = set(['2','3','4','5','6','7','8','9','10','1_11'])
delay = .2


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
    time.sleep(delay)

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

    
    global dealer, playerTable, buttonBbox, delay
    
    variables = ReadVars.read_tuples_from_file("Vars.txt")
    dealer = variables.get("dealer", dealer)
    playerTable = variables.get("playerTable", playerTable)
    buttonBbox = variables.get("buttonBbox", buttonBbox)
    dynamic_dealer = variables.get("dynamicDealer")
    specific_card = variables.get("specificCard")
    surrender15Specific = variables.get("surrender15Specific")
    delay = variables.get("delay")

    keyboard.add_hotkey("F8", toggle_running)
    print("Press F8 to start/stop script. Press ESC to exit.")
    
    attempted_unavailale_surrender = False
    
    while True:
        if not running:
            time.sleep(0.)
            if keyboard.is_pressed("esc"):
                print("Exiting script.")
                break
            continue
        
        # Emergency stop
        if keyboard.is_pressed("esc"):
            print("Exiting script.")
            break

        
        

        
        buttons = ButtonChecker.check_buttons(bbox=buttonBbox)
        time.sleep(delay)
        
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
                playerLoc = OCR.find_player.detect_boxes(bbox=playerTable, mode='player')[0][0]
            except:
                continue

            player_text = str(OCR.ocr_card(playerLoc, mode='player'))
            if dynamic_dealer == 1:
                try:
                    dealer_text = str(OCR.ocr_card(
                        OCR.find_player.detect_boxes(bbox=dealer, mode='dealer')[0][0]
                    ))
                except Exception as e:
                    print(f"Failed ocr for dealer (dynamic): {e}, skipping loop")
                    continue
            elif dynamic_dealer == 0:
                try:
                    dealer_text = str(OCR.ocr_card(dealer))
                except Exception as e:
                    print(f"Failed ocr for dealer (static): {e}, skipping loop")
                    continue
            
            if dealer_text not in valid_dealer:
                print(f"Invalid dealer OCR: {dealer_text}, skipping loop")
                continue

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
                    time.sleep(1)  # wait for split to process
                    buttons = ButtonChecker.check_buttons(bbox=buttonBbox)
                    while "HitAvailable.PNG" not in buttons:
                        print("Waiting for buttons to load after split")
                        time.sleep(0.1)
                        buttons = ButtonChecker.check_buttons(bbox=buttonBbox)
                    continue
            if player_text == "2_12" and "SplitAvailable.PNG" not in buttons:
                print("Split button not detected for some reason, continuing")
                continue

            # --- Surrender Logic ---
            if "_" not in player_text and ("SurrenderAvailable.PNG" in buttons):
                surrenderAction = surrender.loc[surrender["Hand"] == player_text, dealer_text].values[0]
                if surrenderAction and "SurrenderAvailable.PNG" in buttons:
                    if player_text == "15" and dealer_text == "10" and surrender15Specific == 1:
                        try:
                            specific_card = OCR.ocr_specific_card(specific_card)
                        except:
                            print("Failed ocr for specific card, skipping loop")
                            continue
                        if specific_card == "8" or specific_card == "7":
                            print("Not surrendering on 15 vs 10 with 6 or 8")
                            print("Hitting instead")
                            last_print = "Hitting instead"
                            if "HitAvailable.PNG" not in buttons:
                                continue
                            buttonClicker(buttons["HitAvailable.PNG"],bbox=buttonBbox)
                            continue
                    print("Surrender button detected, surrendering")
                    last_print = "Surrendering"
                    if "SurrenderAvailable.PNG" not in buttons:
                        continue
                    buttonClicker(buttons["SurrenderAvailable.PNG"],bbox=buttonBbox)
                    continue
                # elif surrenderAction and "SurrenderUnavailable.PNG" in buttons and not attempted_unavailale_surrender:
                #     print("Surrender button not detected, trying anyways")
                #     last_print = "Surrender button not detected, trying anyways"
                #     if "SurrenderUnavailable.PNG" not in buttons:
                #         continue
                #     buttonClicker(buttons["SurrenderUnavailable.PNG"],bbox=buttonBbox)
                #     attempted_unavailale_surrender = True
                #     continue

            # --- Soft Hands Logic ---
            if "_" in player_text:
                print("In soft action")
                last_print = "In soft action"
                softAction = soft.loc[soft["Hand"] == player_text, dealer_text].values[0]
                if softAction == "D":
                    if "DoubleAvailable.PNG" in buttons:
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
                    if "DoubleAvailable.PNG" in buttons:
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
                    if "DoubleAvailable.PNG" in buttons:
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
    
