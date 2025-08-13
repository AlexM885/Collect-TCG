# ebay_price_checker.py
from your_card_parser_file import parse_pokemon_card
from your_ebay_auth_file import get_ebay_oauth_token
import requests

CLIENT_ID = "YOUR_EBAY_CLIENT_ID"
CLIENT_SECRET = "YOUR_EBAY_CLIENT_SECRET"

def main(image_path):
    # Step 1: Parse the card
    card_name, card_info = parse_pokemon_card(image_path)
    if not card_name or not card_info:
        print("Card details not found.")
        return

    set_number = card_info["number"]

    # Step 2: Get OAuth token
    token = get_ebay_oauth_token(CLIENT_ID, CLIENT_SECRET)

    # Step 3: Fetch sold listings
    sold_data = get_sold_listings(token, card_name, set_number)

    # Step 4: Calculate average price
    avg_price = calculate_average_price(sold_data)
    if avg_price:
        print(f"Average sold price for {card_name} ({set_number}): ${avg_price:.2f}")
    else:
        print("No sold listings found.")

if __name__ == "__main__":
    main("path_to_your_card_image.jpg")