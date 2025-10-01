Requires:
        Pillow
        OpenCV
        numpy
        pandas
        pyautogui
        keyboard

Run from Blackjack Main.py
Make your game maximized, small numbers probably makes the OCR worse, I didn't run full-screen
Place your initial bet manually and click deal, script only clicks on rebet

Set up bounding box varaibles in Blackjack Main.py
Run boundingbox.py to pick bounding boxes
	Drag box around area and press enter, copy tuple into Blackjack Main.py





    F8 to start/stop script
    ESC to exit script
    Set dealer bounding box to the black square of the dealers score, see images in Captured_Cards/dealer
    Set playerTable bounding box to the entire player area, anywhere the golden player total can appear
    Set buttonBbox to box containing all buttons (Rebet, Stand, Hit, Double, Split, Surrender)

    
    Order of Strategy:
        Check if split is optimal -> Check if surrender is optimal -> Check if soft total -> Check if hard total
    
