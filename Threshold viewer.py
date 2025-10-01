import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import ImageGrab

# Example bbox
dealer = (982, 309, 1012, 329)

def show_with_values(bbox):
    screenshot = ImageGrab.grab(bbox=bbox)
    img = np.array(screenshot)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    fig, ax = plt.subplots()
    ax.imshow(gray, cmap='viridis')
    plt.colorbar(ax.imshow(gray, cmap='viridis'), ax=ax, label="Pixel Intensity")

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = int(event.xdata), int(event.ydata)
            if 0 <= y < gray.shape[0] and 0 <= x < gray.shape[1]:
                val = gray[y, x]
                print(f"Clicked at ({x},{y}) → {val}")
                ax.plot(x, y, "rs", markersize=6)
                ax.text(x+5, y-5, f"{val}", color="red", fontsize=8)
                fig.canvas.draw()

    fig.canvas.mpl_connect("button_press_event", onclick)
    plt.title("Click to view pixel intensity")
    plt.show()

show_with_values((975, 686, 1014, 712))