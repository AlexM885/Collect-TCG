import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import quote_plus
import statistics
from PokemonNameExtractor import parse_pokemon_card

class EbayPriceScraper:
    def __init__(self):
        self.session = requests.Session()
        # More realistic headers with additional fields
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        })
        # Add random session cookies to appear more legitimate
        self.session.cookies.update({
            'ebay': f'%5Esbf%3D%23{random.randint(1000000, 9999999)}',
            'dp1': f'{random.randint(100000000, 999999999)}'
        })
    
    def build_search_url(self, query, max_results=50):
        """Build eBay search URL for sold listings"""
        encoded_query = quote_plus(query)
        base_url = "https://www.ebay.com/sch/i.html"
        params = [
            f"_nkw={encoded_query}",
            "LH_Sold=1",
            "LH_Complete=1",
            "_sop=16",  # Sort by newest
            f"_ipg={min(max_results, 240)}",
            "_dmd=1"
        ]
        return f"{base_url}?" + "&".join(params)
    
    def extract_price_from_text(self, price_text):
        """Extract numeric price from price text"""
        if not price_text:
            return None
        price_text = price_text.strip().replace(',', '')
        
        # Handle different price formats
        price_patterns = [
            r'\$\s*([\d,]+\.?\d*)',  # $123.45 or $123
            r'US\s*\$\s*([\d,]+\.?\d*)',  # US $123.45
            r'([\d,]+\.?\d*)\s*\$',  # 123.45$
            r'([\d,]+\.?\d*)'  # Just numbers
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, price_text)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None
    
    def scrape_sold_listings(self, query, max_results=50, delay_range=(2, 5)):
        """Scrape sold listings from eBay with enhanced error handling"""
        print(f"🔍 Searching eBay for: '{query}'")
        url = self.build_search_url(query, max_results)
        print(f"🌐 URL: {url}")
        
        try:
            # Longer delay to avoid rate limiting
            delay = random.uniform(*delay_range)
            print(f"⏳ Waiting {delay:.1f} seconds...")
            time.sleep(delay)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"📊 Response status: {response.status_code}")
            print(f"📏 Response length: {len(response.content)} bytes")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Check if we got a valid eBay page
            title_tag = soup.find('title')
            if title_tag:
                print(f"🏷️ Page title: {title_tag.get_text()[:100]}...")
                if "blocked" in title_tag.get_text().lower() or "robot" in title_tag.get_text().lower():
                    print("🚫 Detected blocking page")
                    return []
            
            # Try multiple selectors for items
            item_selectors = [
                'div.s-item',
                '.s-item',
                'div[data-view="mi:1686|iid:1"]',
                '.srp-results .s-item',
                '.srp-item',
                'li.s-item'
            ]
            
            items = []
            for selector in item_selectors:
                items = soup.select(selector)
                if items:
                    print(f"✅ Found items using selector: {selector}")
                    break
            
            if not items:
                print("❌ No items found with any selector")
                # Debug: Print some of the page structure
                print("🔍 Available classes on page:")
                all_elements = soup.find_all(attrs={"class": True})
                classes = set()
                for el in all_elements[:50]:  # Check first 50 elements
                    if isinstance(el.get('class'), list):
                        classes.update(el.get('class'))
                for cls in sorted(list(classes))[:20]:  # Show first 20 classes
                    print(f"   .{cls}")
                return []
            
            listings = []
            print(f"📦 Found {len(items)} potential items")
            
            processed_count = 0
            for i, item in enumerate(items):
                if processed_count >= max_results:
                    break
                    
                try:
                    # Skip sponsored/ad items
                    if item.find(attrs={'class': re.compile(r'.*ad.*|.*sponsor.*', re.I)}):
                        continue
                    
                    # Try multiple price selectors
                    price_selectors = [
                        '.s-item__price .notranslate',
                        '.s-item__price',
                        'span.notranslate',
                        '.s-item__detail .s-item__price',
                        '[data-testid="price"]',
                        '.price'
                    ]
                    
                    price_element = None
                    for selector in price_selectors:
                        price_element = item.select_one(selector)
                        if price_element:
                            break
                    
                    if not price_element:
                        continue
                        
                    price_text = price_element.get_text(strip=True)
                    price = self.extract_price_from_text(price_text)
                    
                    if not price or price <= 0:
                        continue
                        
                    # Extract title with multiple selectors
                    title_selectors = [
                        '.s-item__title',
                        'h3.s-item__title',
                        '.s-item__link',
                        'a[data-testid="item-title"]',
                        '.s-item__wrapper .s-item__title'
                    ]
                    
                    title_element = None
                    for selector in title_selectors:
                        title_element = item.select_one(selector)
                        if title_element:
                            break
                    
                    title = title_element.get_text(strip=True) if title_element else "Unknown"
                    
                    # Skip items that don't seem relevant
                    if len(title) < 10 or "pokemon" not in title.lower():
                        continue
                    
                    # Extract card details from title
                    card_details = self.parse_card_details(title)
                    
                    listings.append({
                        'price': price,
                        'title': title,
                        'card_name': card_details.get('name', 'Unknown'),
                        'card_type': card_details.get('type', ''),
                        'set_info': card_details.get('set', ''),
                        'year': card_details.get('year', '')
                    })
                    
                    print(f"  💰 ${price:.2f} - {title[:60]}...")
                    processed_count += 1
                
                except Exception as e:
                    print(f"  ⚠️ Error processing item {i}: {e}")
                    continue
            
            print(f"✅ Successfully extracted {len(listings)} valid listings")
            return listings
            
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return []
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return []
    
    def parse_card_details(self, title):
        """Parse card details from listing title"""
        details = {
            'name': 'Unknown',
            'type': '',
            'set': '',
            'year': ''
        }
        
        title_lower = title.lower()
        
        # Common Pokemon card patterns
        pokemon_patterns = [
            r'(charizard|pikachu|blastoise|venusaur|mewtwo|mew|rayquaza|lugia|ho-oh)',
            r'(\w+(?:saur|zard|toise|chu|two|mew))',
            r'(\w+)\s+(?:ex|gx|v|vmax|vstar)',
        ]
        
        for pattern in pokemon_patterns:
            match = re.search(pattern, title_lower)
            if match:
                details['name'] = match.group(1).strip().title()
                break
        
        # Extract card type
        type_patterns = ['ex', 'gx', 'v', 'vmax', 'vstar', 'trainer', 'energy', 'promo', 'holo', 'reverse']
        for pattern in type_patterns:
            if pattern in title_lower:
                details['type'] = pattern.upper()
                break
        
        # Extract set info
        set_patterns = [
            r'(\d+/\d+)',  # Card number
            r'(base set|jungle|fossil|team rocket)',  # Classic sets
            r'(\w+\s+(?:set|series|collection))'
        ]
        
        for pattern in set_patterns:
            match = re.search(pattern, title_lower)
            if match:
                details['set'] = match.group(1).strip()
                break
        
        # Extract year
        year_match = re.search(r'\b(199\d|20[0-2]\d)\b', title)
        if year_match:
            details['year'] = year_match.group(1)
        
        return details
    
    def categorize_card(self, title):
        """Categorize card as Japanese/English and Graded/Ungraded"""
        title_lower = title.lower()
        
        # Check if Japanese
        japanese_keywords = ['japanese', 'japan', 'jpn', 'jp']
        is_japanese = any(keyword in title_lower for keyword in japanese_keywords)
        
        # Check if graded - first check if any grading company is mentioned
        grading_companies = ['cgc', 'bgs', 'psa', 'ace', 'rpa']
        is_graded = False
        grade = None
        
        # Check if any grading company name appears in the title
        for company in grading_companies:
            if company in title_lower:
                is_graded = True
                
                # Try to extract the grade number if it follows the company name
                pattern = rf'{company}\s*(\d+(?:\.\d+)?)'
                match = re.search(pattern, title_lower)
                if match:
                    grade = float(match.group(1))
                else:
                    # If company is mentioned but no grade found, try to find any number that could be a grade
                    # Look for common grade patterns anywhere in the title
                    grade_patterns = [
                        r'\b(10|9\.5|9|8\.5|8|7\.5|7|6\.5|6|5\.5|5|4\.5|4|3\.5|3|2\.5|2|1\.5|1)\b'
                    ]
                    for grade_pattern in grade_patterns:
                        grade_match = re.search(grade_pattern, title_lower)
                        if grade_match:
                            grade = float(grade_match.group(1))
                            break
                break
        
        # Determine category
        if is_japanese and is_graded:
            category = "graded_japanese"
        elif is_japanese and not is_graded:
            category = "japanese"
        elif not is_japanese and is_graded:
            category = "graded_english"
        else:
            category = "english"
        
        return {
            'category': category,
            'is_japanese': is_japanese,
            'is_graded': is_graded,
            'grade': grade
        }
    
    def calculate_price_stats_by_category(self, listings):
        """Calculate price statistics categorized by Japanese/English and Graded/Ungraded"""
        if not listings:
            return {
                "japanese": {"average": None, "median": None, "min": None, "max": None, "count": 0, "listings": []},
                "graded_japanese": {"average": None, "median": None, "min": None, "max": None, "count": 0, "listings": [], "grades": {}},
                "english": {"average": None, "median": None, "min": None, "max": None, "count": 0, "listings": []},
                "graded_english": {"average": None, "median": None, "min": None, "max": None, "count": 0, "listings": [], "grades": {}},
                "total": {"count": 0}
            }
        
        # Categorize all listings
        categorized = {
            "japanese": [],
            "graded_japanese": [],
            "english": [],
            "graded_english": []
        }
        
        grade_breakdown = {
            "graded_japanese": {},
            "graded_english": {}
        }
        
        for listing in listings:
            card_info = self.categorize_card(listing['title'])
            category = card_info['category']
            
            # Add category info to listing
            listing['category'] = category
            listing['is_japanese'] = card_info['is_japanese']
            listing['is_graded'] = card_info['is_graded']
            listing['grade'] = card_info['grade']
            
            categorized[category].append(listing)
            
            # Track grades for graded cards
            if card_info['is_graded'] and card_info['grade'] is not None:
                grade = card_info['grade']
                if grade not in grade_breakdown[category]:
                    grade_breakdown[category][grade] = []
                grade_breakdown[category][grade].append(listing)
        
        # Calculate stats for each category
        results = {}
        for category, category_listings in categorized.items():
            if category_listings:
                prices = [listing['price'] for listing in category_listings]
                prices.sort()
                
                stats = {
                    "average": round(statistics.mean(prices), 2),
                    "median": round(statistics.median(prices), 2),
                    "min": round(min(prices), 2),
                    "max": round(max(prices), 2),
                    "count": len(prices),
                    "listings": category_listings
                }
                
                # Add grade breakdown for graded categories
                if category in ['graded_japanese', 'graded_english']:
                    grades_stats = {}
                    for grade, grade_listings in grade_breakdown[category].items():
                        grade_prices = [listing['price'] for listing in grade_listings]
                        grades_stats[grade] = {
                            "average": round(statistics.mean(grade_prices), 2),
                            "median": round(statistics.median(grade_prices), 2),
                            "min": round(min(grade_prices), 2),
                            "max": round(max(grade_prices), 2),
                            "count": len(grade_prices),
                            "listings": grade_listings
                        }
                    stats["grades"] = grades_stats
                
                results[category] = stats
            else:
                base_stats = {
                    "average": None,
                    "median": None,
                    "min": None,
                    "max": None,
                    "count": 0,
                    "listings": []
                }
                if category in ['graded_japanese', 'graded_english']:
                    base_stats["grades"] = {}
                results[category] = base_stats
        
        results["total"] = {"count": len(listings)}
        return results
    
    def get_card_price_analysis(self, card_name, card_type, set_number, card_year, max_results=30):
        """Get comprehensive price analysis for a Pokemon card"""
        # Build query with better relevance
        query_parts = []
        
        if card_name and card_name.lower() != "unknown":
            query_parts.append(card_name)
        
        if card_type and card_type.lower() not in ["pokemon", "unknown", ""]:
            query_parts.append(card_type)
        
        if set_number:
            query_parts.append(set_number)
        
        query_parts.append("pokemon card")
        
        # Add year if specific
        if card_year:
            query_parts.append(str(card_year))
        
        query = " ".join(filter(None, query_parts))
        
        print(f"\n📊 Optimized Query: '{query}'")
        listings = self.scrape_sold_listings(query, max_results=max_results)
        
        if not listings:
            # Try a simpler query if the first one failed
            simple_query = f"{card_name} pokemon" if card_name else "pokemon card"
            print(f"🔄 Retrying with simpler query: '{simple_query}'")
            listings = self.scrape_sold_listings(simple_query, max_results=max_results)
        
        # Filter listings for better relevance
        if listings and card_name and card_name.lower() != "unknown":
            filtered_listings = []
            card_name_lower = card_name.lower()
            
            for listing in listings:
                title_lower = listing['title'].lower()
                if card_name_lower in title_lower:
                    # Additional filtering for card type if specified
                    if not card_type or card_type.lower() in title_lower or card_type.lower() == "pokemon":
                        filtered_listings.append(listing)
            
            if filtered_listings:
                print(f"🎯 Filtered to {len(filtered_listings)} relevant listings")
                listings = filtered_listings
        
        return self.calculate_price_stats_by_category(listings)

def fetch_sold_price_stats_scraper(card_name, card_type, set_number, card_year):
    """Main function to get price stats using web scraping"""
    scraper = EbayPriceScraper()
    return scraper.get_card_price_analysis(card_name, card_type, set_number, card_year)

def main():
    image_path = r"C:\Users\AlexF\Downloads\venesaurEX.jpg"
    
    # Parse the card
    card_name, card_type, card_info, card_year = parse_pokemon_card(image_path)
    
    print("\n" + "=" * 50)
    print("🔍 PREPARING PRICE SEARCH:")
    print("=" * 50)
    
    name_str = card_name if card_name else "Unknown"
    type_str = card_type if card_type else ""
    set_number_str = card_info.get('number', '') if card_info and isinstance(card_info, dict) else ""
    year_str = str(card_year) if card_year else ""
    
    print(f"🎯 Card Name: '{name_str}'")
    print(f"🏷️ Card Type: '{type_str}'")
    print(f"🔢 Set Number: '{set_number_str}'")
    print(f"📅 Year: '{year_str}'")
    
    if card_name:
        print(f"\n🕷️ Starting enhanced eBay scraping...")
        price_stats = fetch_sold_price_stats_scraper(name_str, type_str, set_number_str, year_str)
        
        print("\n" + "=" * 50)
        print("💰 CATEGORIZED PRICE ANALYSIS:")
        print("=" * 50)
        
        total_found = price_stats.get('total', {}).get('count', 0)
        if total_found > 0:
            print(f"📊 Total Listings Found: {total_found}")
            print()
            
            # Display results for each category
            categories = {
                'english': '🇺🇸 ENGLISH CARDS',
                'japanese': '🇯🇵 JAPANESE CARDS', 
                'graded_english': '🏆 GRADED ENGLISH CARDS',
                'graded_japanese': '🏆 GRADED JAPANESE CARDS'
            }
            
            for category_key, category_name in categories.items():
                category_data = price_stats.get(category_key, {})
                count = category_data.get('count', 0)
                
                if count > 0:
                    print(f"{category_name}")
                    print(f"  📊 Count: {count}")
                    print(f"  💵 Average: ${category_data['average']}")
                    print(f"  📊 Median: ${category_data['median']}")
                    print(f"  📉 Min: ${category_data['min']}")
                    print(f"  📈 Max: ${category_data['max']}")
                    
                    # Show grade breakdown for graded cards
                    if 'grades' in category_data and category_data['grades']:
                        print(f"  🎯 Grade Breakdown:")
                        for grade, grade_data in sorted(category_data['grades'].items(), reverse=True):
                            print(f"    Grade {grade}: {grade_data['count']} cards, Avg: ${grade_data['average']}")
                    
                    print(f"  📋 Sample Listings:")
                    for listing in category_data['listings'][:3]:  # Show first 3
                        grade_info = f" (Grade {listing['grade']})" if listing['is_graded'] and listing['grade'] else ""
                        print(f"    💰 ${listing['price']:.2f}{grade_info}")
                        print(f"    📜 {listing['title'][:50]}...")
                    print()
                else:
                    print(f"{category_name}: No listings found")
                    print()
            
            # Summary comparison
            print("📊 CATEGORY COMPARISON:")
            print("-" * 30)
            for category_key, category_name in categories.items():
                category_data = price_stats.get(category_key, {})
                if category_data.get('count', 0) > 0:
                    avg = category_data['average']
                    print(f"{category_name}: ${avg} avg ({category_data['count']} listings)")
        else:
            print("❌ No price data found in any category")
            print("💡 Troubleshooting suggestions:")
            print("   - Check if card name is correct")
            print("   - Try manual eBay search to verify listings exist")
            print("   - eBay may be blocking automated requests")
            print("   - Try again after a longer delay")
    else:
        print("❌ Cannot scrape prices - no card name detected")

if __name__ == "__main__":
    main()