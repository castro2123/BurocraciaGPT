import cv2
import numpy as np
import easyocr
from PIL import Image

reader = easyocr.Reader(['pt', 'en'], gpu=False)

def extract_image_text(file):

    image = Image.open(file).convert("RGB")
    image = np.array(image)

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    result = reader.readtext(gray, detail=0)

    return "\n".join(result)