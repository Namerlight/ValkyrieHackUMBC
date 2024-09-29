import os
from PIL import Image, ImageGrab

def grab_screen():
    if not os.path.exists("temp_imgs"):
        os.makedirs("temp_imgs")

    img = ImageGrab.grab()
    img = img.resize((854, 480), Image.NEAREST)
    img.save(os.path.join("temp_imgs", "current_image.jpeg"))
