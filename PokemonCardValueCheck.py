import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import statistics
from datetime import datetime, timedelta

# Import your existing functions
from PokemonNameExtractor import parse_pokemon_card

class PokemonCardValueChecker:
    def __init__(self):
        self.session = requests.Session()
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def search_ebay_sold_listings(self, pokemon_name, card_number=None, max_results=20):
        """Search eBay for sold listings of a Pokemon card"""
        print(f"🔍 Searching eBay sold listings for {pokemon_name}...")
        
        # Build search query
        search_terms = [pokemon_name, "pokemon", "card"]
        if card_number:
            # Extract just the card number part (before the /)
            card_num = card_number.split('/')[0] if '/' in card_number else card_number
            search_terms.append(card_num)
        
        query = " ".join(search_terms)
        encoded_query = quote_plus(query)
        
        # eBay sold listings URL
        url = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={encoded_query}&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1"
        
        try:
            print(f"📡 Fetching: {url[:100]}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find sold listing items
            items = soup.find_all('div', class_='s-item__wrapper clearfix')
            
            sold_prices = []
            listings_info = []
            
            print(f"🏷️  Found {len(items)} potential listings")
            
            for item in items[:max_results]:
                try:
                    # Get title
                    title_elem = item.find('h3', class_='s-item__title')
                    title = title_elem.get_text(strip=True) if title_elem else "No title"
                    
                    # Skip sponsored items or irrelevant listings
                    if "sponsored" in title.lower() or not self._is_relevant_listing(title, pokemon_name):
                        continue
                    
                    # Get price
                    price_elem = item.find('span', class_='s-item__price')
                    if not price_elem:
                        continue
                    
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price(price_text)
                    
                    if price and 1 <= price <= 10000:  # Reasonable price range
                        # Get sold date
                        date_elem = item.find('span', class_='s-item__endedDate')
                        sold_date = date_elem.get_text(strip=True) if date_elem else "Unknown date"
                        
                        sold_prices.append(price)
                        listings_info.append({
                            'title': title[:80] + "..." if len(title) > 80 else title,
                            'price': price,
                            'sold_date': sold_date
                        })
                        
                        print(f"  💰 ${price:.2f} - {title[:50]}...")
                
                except Exception as e:
                    print(f"  ⚠️  Error parsing listing: {e}")
                    continue
            
            return sold_prices, listings_info
            
        except requests.RequestException as e:
            print(f"❌ Error fetching eBay data: {e}")
            return [], []
        except Exception as e:
            print(f"❌ Error parsing eBay response: {e}")
            return [], []

    def _is_relevant_listing(self, title, pokemon_name):
        """Check if the listing title is relevant to our Pokemon card"""
        title_lower = title.lower()
        pokemon_lower = pokemon_name.lower()
        
        # Must contain Pokemon name and "pokemon" or "card"
        has_pokemon_name = pokemon_lower in title_lower
        has_card_indicator = any(keyword in title_lower for keyword in ['pokemon', 'card', 'tcg', 'trading'])
        
        # Filter out obviously irrelevant items
        irrelevant_keywords = ['lot', 'bulk', 'booster', 'pack', 'box', 'binder', 'sleeve', 'case']
        is_irrelevant = any(keyword in title_lower for keyword in irrelevant_keywords)
        
        return has_pokemon_name and has_card_indicator and not is_irrelevant

    def _extract_price(self, price_text):
        """Extract numeric price from price text"""
        # Remove currency symbols and extra text
        price_text = re.sub(r'[^\d.,]', '', price_text)
        
        # Handle different price formats
        if not price_text:
            return None
        
        try:
            # Remove commas and convert to float
            price = float(price_text.replace(',', ''))
            return price
        except ValueError:
            return None

    def calculate_card_value(self, pokemon_name, card_number=None):
        """Calculate the average value of a Pokemon card based on sold listings"""
        print("=" * 60)
        print("💳 POKEMON CARD VALUE CHECKER")
        print("=" * 60)
        
        if card_number:
            print(f"🐾 Pokemon: {pokemon_name}")
            print(f"🔢 Card Number: {card_number}")
        else:
            print(f"🐾 Pokemon: {pokemon_name}")
            print("🔢 Card Number: Not specified")
        
        print()
        
        # Add delay to be respectful to eBay
        time.sleep(1)
        
        # Search eBay sold listings
        sold_prices, listings_info = self.search_ebay_sold_listings(pokemon_name, card_number)
        
        if not sold_prices:
            print("❌ No sold listings found or unable to extract prices")
            return None
        
        # Calculate statistics
        avg_price = statistics.mean(sold_prices)
        median_price = statistics.median(sold_prices)
        min_price = min(sold_prices)
        max_price = max(sold_prices)
        
        print(f"\n📊 PRICE ANALYSIS ({len(sold_prices)} sold listings):")
        print("-" * 40)
        print(f"💰 Average Price: ${avg_price:.2f}")
        print(f"📈 Median Price:  ${median_price:.2f}")
        print(f"🔻 Lowest Price:  ${min_price:.2f}")
        print(f"🔺 Highest Price: ${max_price:.2f}")
        
        # Show recent listings
        if listings_info:
            print(f"\n📋 RECENT SOLD LISTINGS:")
            print("-" * 40)
            for i, listing in enumerate(listings_info[:10], 1):
                print(f"{i:2d}. ${listing['price']:6.2f} - {listing['title']}")
                if listing['sold_date'] != "Unknown date":
                    print(f"     Sold: {listing['sold_date']}")
        
        return {
            'average_price': avg_price,
            'median_price': median_price,
            'min_price': min_price,
            'max_price': max_price,
            'sample_size': len(sold_prices),
            'listings': listings_info
        }

def main():
    """Main function to parse card and get value"""
    # Path to your Pokemon card image
    image_path = r"C:\Users\AlexF\Downloads\venesaurEX.jpg"
    
    print("🎴 POKEMON CARD ANALYZER & VALUE CHECKER")
    print("=" * 60)
    print()
    
    # Parse the card using your existing code
    print("STEP 1: Parsing Pokemon Card")
    print("-" * 30)
    pokemon_name, card_info = parse_pokemon_card(image_path)
    
    if not pokemon_name:
        print("❌ Could not identify Pokemon from card. Exiting.")
        return
    
    print(f"\n✅ Successfully identified: {pokemon_name}")
    card_number = card_info['number'] if card_info else None
    if card_number:
        print(f"✅ Card number: {card_number}")
    
    print(f"\nSTEP 2: Finding Market Value")
    print("-" * 30)
    
    # Get card value
    value_checker = PokemonCardValueChecker()
    value_data = value_checker.calculate_card_value(pokemon_name, card_number)
    
    if value_data:
        print(f"\n🎯 ESTIMATED CARD VALUE: ${value_data['average_price']:.2f}")
        print(f"   (Based on {value_data['sample_size']} recent sold listings)")
    else:
        print("\n❌ Unable to determine card value")

def check_specific_card(pokemon_name, card_number=None):
    """Function to check value of a specific card without image parsing"""
    value_checker = PokemonCardValueChecker()
    return value_checker.calculate_card_value(pokemon_name, card_number)

if __name__ == "__main__":
    main()
    
    # Example of checking specific cards
    print("\n" + "=" * 60)
    print("💡 ADDITIONAL EXAMPLES")
    print("=" * 60)
    
    # You can also check specific cards directly:
    # check_specific_card("Charizard", "4/102")
    # check_specific_card("Pikachu")