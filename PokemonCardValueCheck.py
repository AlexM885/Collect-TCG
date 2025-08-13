import requests
from PokemonNameExtractor import parse_pokemon_card

rapidapi_key = "3243b57cdamshcf052a29ea77b33p131272jsn608fc7a50c63"

def fetch_sold_price_stats(card_name, card_type, set_number, card_year, rapidapi_key):
    url = "https://ebay-average-selling-price.p.rapidapi.com/findCompletedItems"
    query = f"{card_name} {card_type} {set_number} {card_year} English"
    print(f"Query: {query}")
    
    headers = {
        "content-type": "application/json",
        "x-rapidapi-host": "ebay-average-selling-price.p.rapidapi.com",
        "x-rapidapi-key": rapidapi_key
    }
    body = {
        "keywords": query,
        "max_search_results": 100,
        # "category_id": "...", optional
        # "remove_outliers": "true",
        # "site_id": "0"
    }
    resp = requests.post(url, headers=headers, json=body)
    data = resp.json()
    print(data)
    return {
        "average": data.get("average_price"),
        "min": data.get("min_price"),
        "max": data.get("max_price"),
        "count": data.get("total_results")
    }

def main():
    image_path = r"C:\Users\AlexF\Downloads\venesaurEX.jpg"
    
    # Parse the card - returns 4 values
    card_name, card_type, card_info, card_year = parse_pokemon_card(image_path)
    
    print("\n" + "=" * 50)
    print("🔍 PREPARING API QUERY:")
    print("=" * 50)
    
    # Extract the actual string values for the API query
    name_str = card_name if card_name else "Unknown"
    type_str = card_type if card_type else ""
    
    # Extract set number from card_info dictionary
    if card_info and isinstance(card_info, dict):
        set_number_str = card_info.get('number', '')
        print(f"📋 Set Number: {set_number_str}")
    else:
        set_number_str = ""
        print("📋 Set Number: Not found")
    
    year_str = str(card_year) if card_year else ""
    
    print(f"🎯 Card Name: '{name_str}'")
    print(f"🏷️ Card Type: '{type_str}'")
    print(f"🔢 Set Number: '{set_number_str}'")
    print(f"📅 Year: '{year_str}'")
    
    # Only make API call if we have at least a card name
    if card_name:
        print(f"\n🌐 Making API call...")
        price_stats = fetch_sold_price_stats(name_str, type_str, set_number_str, year_str, rapidapi_key)
        
        print("\n" + "=" * 50)
        print("💰 PRICE RESULTS:")
        print("=" * 50)
        print(f"Average Price: ${price_stats.get('average', 'N/A')}")
        print(f"Min Price: ${price_stats.get('min', 'N/A')}")
        print(f"Max Price: ${price_stats.get('max', 'N/A')}")
        print(f"Total Results: {price_stats.get('count', 'N/A')}")
    else:
        print("❌ Cannot make API call - no card name detected")

if __name__ == "__main__":
    main()