import requests
import json
from typing import Dict, List, Optional
import time
import re
from bs4 import BeautifulSoup
import urllib.parse

class PokemonTCGAPI:
    """
    Uses the free Pokemon TCG API (pokemontcg.io) 
    Provides card data but limited pricing info
    """
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.pokemontcg.io/v2"
        self.headers = {'X-Api-Key': api_key} if api_key else {}
    
    def search_cards(self, name: str, number: str = None, set_name: str = None) -> List[Dict]:
        """Search for Pokemon cards"""
        query_parts = [f'name:"{name}"']
        
        if number:
            # Extract card number (before slash)
            card_num = number.split('/')[0]
            query_parts.append(f'number:{card_num}')
        
        if set_name:
            query_parts.append(f'set.name:"{set_name}"')
        
        query = ' '.join(query_parts)
        
        params = {
            'q': query,
            'pageSize': 20
        }
        
        try:
            response = requests.get(f"{self.base_url}/cards", params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except Exception as e:
            print(f"Pokemon TCG API error: {e}")
            return []
    
    def get_card_info(self, name: str, number: str = None):
        """Get basic card information"""
        cards = self.search_cards(name, number)
        
        if not cards:
            return None
        
        card = cards[0]  # Take first match
        return {
            'name': card.get('name'),
            'set_name': card.get('set', {}).get('name'),
            'number': card.get('number'),
            'rarity': card.get('rarity'),
            'artist': card.get('artist'),
            'image_url': card.get('images', {}).get('large'),
            'tcgplayer_url': card.get('tcgplayer', {}).get('url'),
            'cardmarket_url': card.get('cardmarket', {}).get('url'),
            # Limited pricing from Pokemon TCG API
            'tcgplayer_prices': card.get('tcgplayer', {}).get('prices', {}),
            'cardmarket_prices': card.get('cardmarket', {}).get('prices', {})
        }

class EBayPricingScraper:
    """
    Scrapes eBay sold listings for pricing data
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_sold_listings_price(self, pokemon_name: str, card_number: str = None, condition: str = "near mint") -> Dict:
        """Get average price from eBay sold listings"""
        
        # Construct search query
        search_terms = [pokemon_name, "pokemon card"]
        if card_number:
            search_terms.append(card_number)
        if condition:
            search_terms.append(condition)
        
        query = ' '.join(search_terms)
        encoded_query = urllib.parse.quote(query)
        
        # eBay sold listings URL
        url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}&_sacat=0&LH_Sold=1&LH_Complete=1&_sop=13"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find sold price elements
            price_elements = soup.find_all(['span', 'div'], class_=re.compile(r'notranslate'))
            prices = []
            
            for element in price_elements:
                text = element.get_text(strip=True)
                if '$' in text:
                    # Extract price using regex
                    price_match = re.search(r'\$(\d+\.?\d*)', text)
                    if price_match:
                        price = float(price_match.group(1))
                        if 0.50 <= price <= 10000:  # Reasonable price range
                            prices.append(price)
            
            if prices:
                prices = sorted(prices)
                return {
                    'average_price': sum(prices) / len(prices),
                    'median_price': prices[len(prices)//2],
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'sample_size': len(prices),
                    'source': 'eBay Sold Listings'
                }
            
        except Exception as e:
            print(f"eBay scraping error: {e}")
        
        return None

class PriceChartingAPI:
    """
    Alternative: PriceCharting.com has an API (paid but cheaper than TCGPlayer)
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.pricecharting.com/api"
    
    def search_product(self, pokemon_name: str, card_number: str = None):
        """Search for Pokemon card on PriceCharting"""
        query = f"{pokemon_name} Pokemon"
        if card_number:
            query += f" {card_number}"
        
        params = {
            't': self.api_key,
            'q': query,
            'format': 'json'
        }
        
        try:
            response = requests.get(f"{self.base_url}/product", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"PriceCharting API error: {e}")
            return None

class MultiplePricingService:
    """
    Combines multiple pricing sources for better accuracy
    """
    def __init__(self, pokemon_tcg_api_key: str = None, pricecharting_api_key: str = None):
        self.pokemon_api = PokemonTCGAPI(pokemon_tcg_api_key)
        self.ebay_scraper = EBayPricingScraper()
        self.pricecharting = PriceChartingAPI(pricecharting_api_key) if pricecharting_api_key else None
    
    def get_comprehensive_pricing(self, pokemon_name: str, card_number: str = None) -> Dict:
        """Get pricing from multiple sources"""
        print(f"🔍 Searching for pricing: {pokemon_name}" + (f" #{card_number}" if card_number else ""))
        
        results = {
            'pokemon_name': pokemon_name,
            'card_number': card_number,
            'sources': {}
        }
        
        # 1. Pokemon TCG API (basic info + some pricing)
        print("📊 Checking Pokemon TCG API...")
        tcg_info = self.pokemon_api.get_card_info(pokemon_name, card_number)
        if tcg_info:
            results['card_info'] = tcg_info
            
            # Extract TCGPlayer prices if available
            tcg_prices = tcg_info.get('tcgplayer_prices', {})
            if tcg_prices:
                results['sources']['tcgplayer_via_pokemon_api'] = tcg_prices
        
        # 2. eBay sold listings
        print("🛒 Checking eBay sold listings...")
        ebay_pricing = self.ebay_scraper.get_sold_listings_price(pokemon_name, card_number)
        if ebay_pricing:
            results['sources']['ebay_sold'] = ebay_pricing
        
        # 3. PriceCharting (if API key provided)
        if self.pricecharting:
            print("📈 Checking PriceCharting...")
            pc_result = self.pricecharting.search_product(pokemon_name, card_number)
            if pc_result:
                results['sources']['pricecharting'] = pc_result
        
        # Calculate consensus pricing
        prices = []
        
        # Extract prices from different sources
        if 'ebay_sold' in results['sources']:
            prices.append(results['sources']['ebay_sold']['average_price'])
        
        if 'tcgplayer_via_pokemon_api' in results['sources']:
            tcg_prices = results['sources']['tcgplayer_via_pokemon_api']
            for condition, price_data in tcg_prices.items():
                if isinstance(price_data, dict) and 'market' in price_data:
                    prices.append(price_data['market'])
        
        if prices:
            results['consensus'] = {
                'average_price': sum(prices) / len(prices),
                'price_range': f"${min(prices):.2f} - ${max(prices):.2f}",
                'sources_count': len(prices)
            }
        
        return results

# Free alternative using web scraping
class TCGPlayerScraper:
    """
    Scrapes TCGPlayer directly (use responsibly - respect rate limits)
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.tcgplayer.com"
    
    def search_card_price(self, pokemon_name: str, card_number: str = None):
        """Search and scrape TCGPlayer for card prices"""
        
        query = f"{pokemon_name} pokemon"
        if card_number:
            query += f" {card_number}"
        
        search_url = f"{self.base_url}/search/pokemon/product"
        params = {
            'productLineName': 'pokemon',
            'q': query,
            'view': 'grid'
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This would need to be updated based on TCGPlayer's current HTML structure
            # TCGPlayer frequently changes their structure to prevent scraping
            
            print("⚠️ TCGPlayer scraping requires frequent updates due to anti-scraping measures")
            return None
            
        except Exception as e:
            print(f"TCGPlayer scraping error: {e}")
            return None

def example_usage():
    """Example of how to use the alternative pricing services"""
    
    # Initialize the multiple pricing service
    pricing_service = MultiplePricingService()
    
    # Example card
    pokemon_name = "Charizard"
    card_number = "4/102"
    
    # Get comprehensive pricing
    pricing_data = pricing_service.get_comprehensive_pricing(pokemon_name, card_number)
    
    print("\n" + "=" * 60)
    print("💰 PRICING RESULTS")
    print("=" * 60)
    
    if 'card_info' in pricing_data:
        info = pricing_data['card_info']
        print(f"🎴 Card: {info['name']}")
        print(f"📦 Set: {info['set_name']}")
        print(f"🎯 Number: {info['number']}")
        print(f"✨ Rarity: {info['rarity']}")
        if info.get('image_url'):
            print(f"🖼️ Image: {info['image_url']}")
    
    print(f"\n📊 PRICING SOURCES:")
    for source, data in pricing_data.get('sources', {}).items():
        print(f"\n🔹 {source.replace('_', ' ').title()}:")
        if source == 'ebay_sold':
            print(f"   Average: ${data['average_price']:.2f}")
            print(f"   Range: ${data['min_price']:.2f} - ${data['max_price']:.2f}")
            print(f"   Sample size: {data['sample_size']} sales")
        else:
            print(f"   Data: {data}")
    
    if 'consensus' in pricing_data:
        consensus = pricing_data['consensus']
        print(f"\n🎯 CONSENSUS PRICE:")
        print(f"   Average: ${consensus['average_price']:.2f}")
        print(f"   Range: {consensus['price_range']}")
        print(f"   Based on {consensus['sources_count']} source(s)")

if __name__ == "__main__":
    example_usage()