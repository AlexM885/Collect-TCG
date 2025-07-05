import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_card(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Resize image
    scale = 3  # or 3 if needed
    resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
    
    text = pytesseract.image_to_string(thresh)
    return text

# Test it on a sample image
if __name__ == "__main__":
    path = r"C:\Users\AlexF\Downloads\Charizard_sample_card.jpg"  # Replace with your card image path
    result = extract_text_from_card(path)
    print("Extracted Text:\n", result)