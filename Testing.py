from PIL import Image, ImageEnhance, ImageFilter
from pytesseract import pytesseract
import re
import cv2
import numpy as np

def preprocess_for_results_7_and_15(image_path):
    """Only the preprocessing methods needed for results 7 and 15"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Method 1: Adaptive threshold
    thresh1 = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
    )
    
    # Method 2: OTSU thresholding  
    _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Method 3: Manual threshold
    _, thresh3 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Method 4: Raw grayscale
    raw_gray = gray
    
    return [thresh1, thresh2, thresh3, raw_gray]

def extract_with_results_7_and_15_configs(processed_images):
    """Use the EXACT configurations from the identification code for results 7 and 15 - Returns combined text string"""
    
    # PLACEHOLDER - Replace these with the exact values from your identification run:
    result_7_img_index = 1  # Replace with actual index from identification
    result_7_config = r'--oem 3 --psm 11'  # Replace with exact config from identification
    
    result_15_img_index = 3  # Replace with actual index from identification
    result_15_config = r'--oem 3 --psm 11'  # Replace with exact config from identification
    
    combined_text = ""
    
    # Extract text from result 7 configuration
    try:
        text_7 = pytesseract.image_to_string(processed_images[result_7_img_index], config=result_7_config)
        if text_7.strip():
            combined_text += text_7.strip() + "\n"
    except Exception as e:
        print(f"Error in result 7: {str(e)}")
    
    # Extract text from result 15 configuration  
    try:
        text_15 = pytesseract.image_to_string(processed_images[result_15_img_index], config=result_15_config)
        if text_15.strip():
            combined_text += text_15.strip() + "\n"
    except Exception as e:
        print(f"Error in result 15: {str(e)}")
    
    return combined_text.strip()

def get_ocr_text(image_path):
    """Main function to extract OCR text from image"""
    # Configuration
    path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pytesseract.tesseract_cmd = path_to_tesseract
    
    # Preprocess image 
    processed_images = preprocess_for_results_7_and_15(image_path)
    
    # Extract text using optimized configurations
    ocr_text = extract_with_results_7_and_15_configs(processed_images)
    
    return ocr_text