import requests
from PokemonNameExtractor import parse_pokemon_card

rapidapi_key = "3243b57cdamshcf052a29ea77b33p131272jsn608fc7a50c63"
def fetch_sold_price_stats(card_name, set_number, rapidapi_key):
    url = "https://ebay-average-selling-price.p.rapidapi.com/findCompletedItems"
    query = f"{card_name} {set_number} English"
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
    card_name, card_info = parse_pokemon_card(image_path)
    fetch_sold_price_stats(card_name, card_info, rapidapi_key)

if __name__ == "__main__":
    main()