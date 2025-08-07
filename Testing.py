import cv2
import pytesseract

def get_ocr_text(image_path):
    """Minimal OCR text extraction"""
    # Set Tesseract path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Load and preprocess image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Scale up for better OCR (most important preprocessing step)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    
    # Try two most effective approaches and combine results
    combined_text = ""
    
    try:
        # OTSU thresholding (usually most effective)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text1 = pytesseract.image_to_string(thresh, config='--oem 3 --psm 11')
        if text1.strip():
            combined_text += text1.strip() + "\n"
    except:
        pass
    
    try:
        # Raw grayscale as backup
        text2 = pytesseract.image_to_string(gray, config='--oem 3 --psm 11')
        if text2.strip():
            combined_text += text2.strip() + "\n"
    except:
        pass
    
    return combined_text.strip()