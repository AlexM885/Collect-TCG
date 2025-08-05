from PIL import Image
from pytesseract import pytesseract
import re

#path to tesseract.exe and img
path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
image_path =  r"C:\Users\AlexF\Downloads\Charizard_sample_card.jpg"

#create image obj
img = Image.open(image_path)

#providing the tesseract executable location to pytesseract library
pytesseract.tesseract_cmd = path_to_tesseract

#turn to string
text = pytesseract.image_to_string(img)

#displaying the extracted text
print(text[:-1])

# Extract Pokemon card number (format: number/total)
def extract_pokemon_number(text):
    # Pattern to match number/number format
    pattern = r'\b(\d+)/(\d+)\b'
    
    # Find all matches
    matches = re.findall(pattern, text)
    
    if matches:
        # Return the last match (usually the card number is at the end)
        card_num, total_cards = matches[-1]
        return f"{card_num}/{total_cards}", int(card_num), int(total_cards)
    else:
        return None, None, None

# Extract the card number
card_number, card_num, total_cards = extract_pokemon_number(text)

if card_number:
    print(f"Pokemon Card Number: {card_number}")
else:
    print("No Pokemon card number found in the format 'X/Y'")


extract_pokemon_number(text)
