import cv2
import pytesseract
from PIL import Image


def extract_text_from_card(image_path):
    image = cv2.imread(image_path) #load image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # turn to gray

    text = pytesseract.image_to_string(gray) # get all text
    print("Extracted Text:", text) #print text
    return text 