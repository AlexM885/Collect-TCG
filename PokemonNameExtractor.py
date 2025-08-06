
import re
from Testing import get_ocr_text

POKEMON_NAMES = [
    "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", 
    "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree", 
    "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot", "Rattata", 
    "Raticate", "Spearow", "Fearow", "Ekans", "Arbok", "Pikachu", "Raichu", 
    "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina", "Nidoqueen", "Nidoran♂", 
    "Nidorino", "Nidoking", "Clefairy", "Clefable", "Vulpix", "Ninetales", 
    "Jigglypuff", "Wigglytuff", "Zubat", "Golbat", "Oddish", "Gloom", "Vileplume", 
    "Paras", "Parasect", "Venonat", "Venomoth", "Diglett", "Dugtrio", "Meowth", 
    "Persian", "Psyduck", "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine", 
    "Poliwag", "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop", 
    "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool", 
    "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke", 
    "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel", 
    "Dewgong", "Grimer", "Muk", "Shellder", "Cloyster", "Gastly", "Haunter", 
    "Gengar", "Onix", "Drowzee", "Hypno", "Krabby", "Kingler", "Voltorb", 
    "Electrode", "Exeggcute", "Exeggutor", "Cubone", "Marowak", "Hitmonlee", 
    "Hitmonchan", "Lickitung", "Koffing", "Weezing", "Rhyhorn", "Rhydon", 
    "Chansey", "Tangela", "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking", 
    "Staryu", "Starmie", "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar", 
    "Pinsir", "Tauros", "Magikarp", "Gyarados", "Lapras", "Ditto", "Eevee", 
    "Vaporeon", "Jolteon", "Flareon", "Porygon", "Omanyte", "Omastar", "Kabuto", 
    "Kabutops", "Aerodactyl", "Snorlax", "Articuno", "Zapdos", "Moltres", 
    "Dratini", "Dragonair", "Dragonite", "Mewtwo", "Mew", "Chikorita", "Bayleef", 
    "Meganium", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", 
    "Feraligatr", "Sentret", "Furret", "Hoothoot", "Noctowl", "Ledyba", "Ledian", 
    "Spinarak", "Ariados", "Crobat", "Chinchou", "Lanturn", "Pichu", "Cleffa", 
    "Igglybuff", "Togepi", "Togetic", "Natu", "Xatu", "Mareep", "Flaaffy", 
    "Ampharos", "Bellossom", "Marill", "Azumarill", "Sudowoodo", "Politoed", 
    "Hoppip", "Skiploom", "Jumpluff", "Aipom", "Sunkern", "Sunflora", "Yanma", 
    "Wooper", "Quagsire", "Espeon", "Umbreon", "Murkrow", "Slowking", "Misdreavus", 
    "Unown", "Wobbuffet", "Girafarig", "Pineco", "Forretress", "Dunsparce", 
    "Gligar", "Steelix", "Snubbull", "Granbull", "Qwilfish", "Scizor", "Shuckle", 
    "Heracross", "Sneasel", "Teddiursa", "Ursaring", "Slugma", "Magcargo", 
    "Swinub", "Piloswine", "Corsola", "Remoraid", "Octillery", "Delibird", 
    "Mantine", "Skarmory", "Houndour", "Houndoom", "Kingdra", "Phanpy", "Donphan", 
    "Porygon2", "Stantler", "Smeargle", "Tyrogue", "Hitmontop", "Smoochum", 
    "Elekid", "Magby", "Miltank", "Blissey", "Raikou", "Entei", "Suicune", 
    "Larvitar", "Pupitar", "Tyranitar", "Lugia", "Ho-Oh", "Celebi", "Treecko", 
    "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", 
    "Marshtomp", "Swampert", "Poochyena", "Mightyena", "Zigzagoon", "Linoone", 
    "Wurmple", "Silcoon", "Beautifly", "Cascoon", "Dustox", "Lotad", "Lombre", 
    "Ludicolo", "Seedot", "Nuzleaf", "Shiftry", "Taillow", "Swellow", "Wingull", 
    "Pelipper", "Ralts", "Kirlia", "Gardevoir", "Surskit", "Masquerain", 
    "Shroomish", "Breloom", "Slakoth", "Vigoroth", "Slaking", "Nincada", "Ninjask", 
    "Shedinja", "Whismur", "Loudred", "Exploud", "Makuhita", "Hariyama", "Azurill", 
    "Nosepass", "Skitty", "Delcatty", "Sableye", "Mawile", "Aron", "Lairon", 
    "Aggron", "Meditite", "Medicham", "Electrike", "Manectric", "Plusle", "Minun", 
    "Volbeat", "Illumise", "Roselia", "Gulpin", "Swalot", "Carvanha", "Sharpedo", 
    "Wailmer", "Wailord", "Numel", "Camerupt", "Torkoal", "Spoink", "Grumpig", 
    "Spinda", "Trapinch", "Vibrava", "Flygon", "Cacnea", "Cacturne", "Swablu", 
    "Altaria", "Zangoose", "Seviper", "Lunatone", "Solrock", "Barboach", 
    "Whiscash", "Corphish", "Crawdaunt", "Baltoy", "Claydol", "Lileep", "Cradily", 
    "Anorith", "Armaldo", "Feebas", "Milotic", "Castform", "Kecleon", "Shuppet", 
    "Banette", "Duskull", "Dusclops", "Tropius", "Chimecho", "Absol", "Wynaut", 
    "Snorunt", "Glalie", "Spheal", "Sealeo", "Walrein", "Clamperl", "Huntail", 
    "Gorebyss", "Relicanth", "Luvdisc", "Bagon", "Shelgon", "Salamence", "Beldum", 
    "Metang", "Metagross", "Regirock", "Regice", "Registeel", "Latias", "Latios", 
    "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Turtwig", "Grotle", 
    "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", 
    "Empoleon", "Starly", "Staravia", "Staraptor", "Bidoof", "Bibarel", "Kricketot", 
    "Kricketune", "Shinx", "Luxio", "Luxray", "Budew", "Roserade", "Cranidos", 
    "Rampardos", "Shieldon", "Bastiodon", "Burmy", "Wormadam", "Mothim", "Combee", 
    "Vespiquen", "Pachirisu", "Buizel", "Floatzel", "Cherubi", "Cherrim", "Shellos", 
    "Gastrodon", "Ambipom", "Drifloon", "Drifblim", "Buneary", "Lopunny", 
    "Mismagius", "Honchkrow", "Glameow", "Purugly", "Chingling", "Stunky", 
    "Skuntank", "Bronzor", "Bronzong", "Bonsly", "Mime Jr.", "Happiny", "Chatot", 
    "Spiritomb", "Gible", "Gabite", "Garchomp", "Munchlax", "Riolu", "Lucario", 
    "Hippopotas", "Hippowdon", "Skorupi", "Drapion", "Croagunk", "Toxicroak", 
    "Carnivine", "Finneon", "Lumineon", "Mantyke", "Snover", "Abomasnow", 
    "Weavile", "Magnezone", "Lickilicky", "Rhyperior", "Tangrowth", "Electivire", 
    "Magmortar", "Togekiss", "Yanmega", "Leafeon", "Glaceon", "Gliscor", 
    "Mamoswine", "Porygon-Z", "Gallade", "Probopass", "Dusknoir", "Froslass", 
    "Rotom", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Regigigas", 
    "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", 
    "Victini", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", 
    "Oshawott", "Dewott", "Samurott", "Patrat", "Watchog", "Lillipup", "Herdier", 
    "Stoutland", "Purrloin", "Liepard", "Pansage", "Simisage", "Pansear", 
    "Simisear", "Panpour", "Simipour", "Munna", "Musharna", "Pidove", "Tranquill", 
    "Unfezant", "Blitzle", "Zebstrika", "Roggenrola", "Boldore", "Gigalith", 
    "Woobat", "Swoobat", "Drilbur", "Excadrill", "Audino", "Timburr", "Gurdurr", 
    "Conkeldurr", "Tympole", "Palpitoad", "Seismitoad", "Throh", "Sawk", 
    "Sewaddle", "Swadloon", "Leavanny", "Venipede", "Whirlipede", "Scolipede", 
    "Cottonee", "Whimsicott", "Petilil", "Lilligant", "Basculin", "Sandile", 
    "Krokorok", "Krookodile", "Darumaka", "Darmanitan", "Maractus", "Dwebble", 
    "Crustle", "Scraggy", "Scrafty", "Sigilyph", "Yamask", "Cofagrigus", "Tirtouga", 
    "Carracosta", "Archen", "Archeops", "Trubbish", "Garbodor", "Zorua", "Zoroark", 
    "Minccino", "Cinccino", "Gothita", "Gothorita", "Gothitelle", "Solosis", 
    "Duosion", "Reuniclus", "Ducklett", "Swanna", "Vanillite", "Vanillish", 
    "Vanilluxe", "Deerling", "Sawsbuck", "Emolga", "Karrablast", "Escavalier", 
    "Foongus", "Amoonguss", "Frillish", "Jellicent", "Alomomola", "Joltik", 
    "Galvantula", "Ferroseed", "Ferrothorn", "Klink", "Klang", "Klinklang", 
    "Tynamo", "Eelektrik", "Eelektross", "Elgyem", "Beheeyem", "Litwick", 
    "Lampent", "Chandelure", "Axew", "Fraxure", "Haxorus", "Cubchoo", "Beartic", 
    "Cryogonal", "Shelmet", "Accelgor", "Stunfisk", "Mienfoo", "Mienshao", 
    "Druddigon", "Golett", "Golurk", "Pawniard", "Bisharp", "Bouffalant", 
    "Rufflet", "Braviary", "Vullaby", "Mandibuzz", "Heatmor", "Durant", "Deino", 
    "Zweilous", "Hydreigon", "Larvesta", "Volcarona", "Cobalion", "Terrakion", 
    "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", 
    "Kyurem", "Keldeo", "Meloetta", "Genesect", "Chespin", "Quilladin", "Chesnaught", 
    "Fennekin", "Braixen", "Delphox", "Froakie", "Frogadier", "Greninja", "Bunnelby", 
    "Diggersby", "Fletchling", "Fletchinder", "Talonflame", "Scatterbug", "Spewpa", 
    "Vivillon", "Litleo", "Pyroar", "Flabébé", "Floette", "Florges", "Skiddo", 
    "Gogoat", "Pancham", "Pangoro", "Furfrou", "Espurr", "Meowstic", "Honedge", 
    "Doublade", "Aegislash", "Spritzee", "Aromatisse", "Swirlix", "Slurpuff", 
    "Inkay", "Malamar", "Binacle", "Barbaracle", "Skrelp", "Dragalge", "Clauncher", 
    "Clawitzer", "Helioptile", "Heliolisk", "Tyrunt", "Tyrantrum", "Amaura", 
    "Aurorus", "Sylveon", "Hawlucha", "Dedenne", "Carbink", "Goomy", "Sliggoo", 
    "Goodra", "Klefki", "Phantump", "Trevenant", "Pumpkaboo", "Gourgeist", 
    "Bergmite", "Avalugg", "Noibat", "Noivern", "Xerneas", "Yveltal", "Zygarde", 
    "Diancie", "Hoopa", "Volcanion", "Rowlet", "Dartrix", "Decidueye", "Litten", 
    "Torracat", "Incineroar", "Popplio", "Brionne", "Primarina", "Pikipek", 
    "Trumbeak", "Toucannon", "Yungoos", "Gumshoos", "Grubbin", "Charjabug", 
    "Vikavolt", "Crabrawler", "Crabominable", "Oricorio", "Cutiefly", "Ribombee", 
    "Rockruff", "Lycanroc", "Wishiwashi", "Mareanie", "Toxapex", "Mudbray", 
    "Mudsdale", "Dewpider", "Araquanid", "Fomantis", "Lurantis", "Morelull", 
    "Shiinotic", "Salandit", "Salazzle", "Stufful", "Bewear", "Bounsweet", 
    "Steenee", "Tsareena", "Comfey", "Oranguru", "Passimian", "Wimpod", 
    "Golisopod", "Sandygast", "Palossand", "Pyukumuku", "Type: Null", "Silvally", 
    "Minior", "Komala", "Turtonator", "Togedemaru", "Mimikyu", "Bruxish", 
    "Drampa", "Dhelmise", "Jangmo-o", "Hakamo-o", "Kommo-o", "Tapu Koko", 
    "Tapu Lele", "Tapu Bulu", "Tapu Fini", "Cosmog", "Cosmoem", "Solgaleo", 
    "Lunala", "Nihilego", "Buzzwole", "Pheromosa", "Xurkitree", "Celesteela", 
    "Kartana", "Guzzlord", "Necrozma", "Magearna", "Marshadow", "Poipole", 
    "Naganadel", "Stakataka", "Blacephalon", "Zeraora", "Meltan", "Melmetal", 
    "Grookey", "Thwackey", "Rillaboom", "Scorbunny", "Raboot", "Cinderace", 
    "Sobble", "Drizzile", "Inteleon", "Skwovet", "Greedent", "Rookidee", 
    "Corvisquire", "Corviknight", "Blipbug", "Dottler", "Orbeetle", "Nickit", 
    "Thievul", "Gossifleur", "Eldegoss", "Wooloo", "Dubwool", "Chewtle", 
    "Drednaw", "Yamper", "Boltund", "Rolycoly", "Carkol", "Coalossal", "Applin", 
    "Flapple", "Appletun", "Silicobra", "Sandaconda", "Cramorant", "Arrokuda", 
    "Barraskewda", "Toxel", "Toxtricity", "Sizzlipede", "Centiskorch", "Clobbopus", 
    "Grapploct", "Sinistea", "Polteageist", "Hatenna", "Hattrem", "Hatterene", 
    "Impidimp", "Morgrem", "Grimmsnarl", "Obstagoon", "Perrserker", "Cursola", 
    "Sirfetch'd", "Mr. Rime", "Runerigus", "Milcery", "Alcremie", "Falinks", 
    "Pincurchin", "Snom", "Frosmoth", "Stonjourner", "Eiscue", "Indeedee", 
    "Morpeko", "Cufant", "Copperajah", "Dracozolt", "Arctozolt", "Dracovish", 
    "Arctovish", "Duraludon", "Dreepy", "Drakloak", "Dragapult", "Zacian", 
    "Zamazenta", "Eternatus", "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", 
    "Glastrier", "Spectrier", "Calyrex", "Wyrdeer", "Kleavor", "Ursaluna", 
    "Basculegion", "Sneasler", "Overqwil", "Enamorus", "Sprigatito", "Floragato", 
    "Meowscarada", "Fuecoco", "Crocalor", "Skeledirge", "Quaxly", "Quaxwell", 
    "Quaquaval", "Lechonk", "Oinkologne", "Tarountula", "Spidops", "Nymble", 
    "Lokix", "Pawmi", "Pawmo", "Pawmot", "Tandemaus", "Maushold", "Fidough", 
    "Dachsbun", "Smoliv", "Dolliv", "Arboliva", "Squawkabilly", "Nacli", "Naclstack", 
    "Garganacl", "Charcadet", "Armarouge", "Ceruledge", "Tadbulb", "Bellibolt", 
    "Wattrel", "Kilowattrel", "Maschiff", "Mabosstiff", "Shroodle", "Grafaiai", 
    "Bramblin", "Brambleghast", "Toedscool", "Toedscruel", "Klawf", "Capsakid", 
    "Scovillain", "Rellor", "Rabsca", "Flittle", "Espathra", "Tinkatuff", 
    "Tinkaton", "Wiglett", "Wugtrio", "Bombirdier", "Finizen", "Palafin", 
    "Varoom", "Revavroom", "Cyclizar", "Orthworm", "Glimmora", "Greavard", 
    "Houndstone", "Flamigo", "Cetoddle", "Cetitan", "Veluza", "Dondozo", 
    "Tatsugiri", "Annihilape", "Clodsire", "Farigiraf", "Dudunsparce", "Kingambit", 
    "Great Tusk", "Scream Tail", "Brute Bonnet", "Flutter Mane", "Slither Wing", 
    "Sandy Shocks", "Iron Treads", "Iron Bundle", "Iron Hands", "Iron Jugulis", 
    "Iron Moth", "Iron Thorns", "Frigibax", "Arctibax", "Baxcalibur", "Gimmighoul", 
    "Gholdengo", "Wo-Chien", "Chien-Pao", "Ting-Lu", "Chi-Yu", "Roaring Moon", 
    "Iron Valiant", "Koraidon", "Miraidon", "Walking Wake", "Iron Leaves", 
    "Dipplin", "Poltchageist", "Sinistcha", "Okidogi", "Munkidori", "Fezandipiti", 
    "Ogerpon", "Archaludon", "Hydrapple", "Gouging Fire", "Raging Bolt", 
    "Iron Boulder", "Iron Crown", "Terapagos", "Pecharunt"
]





def extract_card_number(text):
    """Extract Pokemon card number from OCR text"""
    patterns = [
        r'\b(\d+)/(\d+)\b',
        r'(\d+)\s*/\s*(\d+)',
        r'(\d+)\/(\d+)',
        r'No\.\s*(\d+)/(\d+)',
        r'#(\d+)/(\d+)',
        r'(\d+)\s*of\s*(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            card_num, total_cards = match
            # Validate the numbers are reasonable for Pokemon cards
            if 1 <= int(card_num) <= 999 and 10 <= int(total_cards) <= 999:
                return {
                    'number': f"{card_num}/{total_cards}",
                    'card_num': int(card_num),
                    'total_cards': int(total_cards)
                }
    return None

def extract_pokemon_name(text):
    """Extract Pokemon name from OCR text using the predefined list - returns first match found by position"""
    # Clean the text for better matching
    text_upper = text.upper()
    lines = text.split('\n')
    
    # Store matches with their position in the text
    position_matches = []
    
    # Check for exact matches first - track position
    for pokemon in POKEMON_NAMES:
        pokemon_upper = pokemon.upper()
        
        # Check if the Pokemon name appears in the text
        if pokemon_upper in text_upper:
            # Find the position of the match
            position = text_upper.find(pokemon_upper)
            
            # Additional validation - make sure it's not part of a larger word
            pattern = r'\b' + re.escape(pokemon_upper) + r'\b'
            if re.search(pattern, text_upper):
                position_matches.append({
                    'name': pokemon,
                    'confidence': 'high',
                    'match_type': 'exact_word_boundary',
                    'position': position
                })
            elif pokemon_upper in text_upper:
                position_matches.append({
                    'name': pokemon,
                    'confidence': 'medium', 
                    'match_type': 'substring_match',
                    'position': position
                })
    
    # If we have exact matches, return the earliest one
    if position_matches:
        # Sort by position (earliest first), then by confidence if positions are equal
        confidence_order = {'high': 3, 'medium': 2, 'low': 1}
        position_matches.sort(key=lambda x: (x['position'], -confidence_order.get(x['confidence'], 0)))
        
        # Remove duplicates by name, keeping the first occurrence
        unique_names = []
        seen_names = set()
        for match in position_matches:
            if match['name'] not in seen_names:
                unique_names.append(match)
                seen_names.add(match['name'])
        
        return unique_names
    
    # If no exact matches, try fuzzy matching on individual lines (check lines in order)
    for line_idx, line in enumerate(lines[:5]):  # Check first 5 lines
        line_clean = line.strip().upper()
        if 3 <= len(line_clean) <= 20:  # Reasonable length for Pokemon names
            for pokemon in POKEMON_NAMES:
                pokemon_upper = pokemon.upper()
                # Check for similar length and partial matches
                if abs(len(line_clean) - len(pokemon_upper)) <= 2:
                    # Simple similarity check
                    matches = sum(1 for a, b in zip(line_clean, pokemon_upper) if a == b)
                    similarity = matches / max(len(line_clean), len(pokemon_upper))
                    if similarity >= 0.7:  # 70% similarity threshold
                        return [{
                            'name': pokemon,
                            'confidence': 'low',
                            'match_type': 'fuzzy_match',
                            'similarity': similarity,
                            'matched_text': line.strip(),
                            'line_number': line_idx
                        }]
    
    return []

def parse_pokemon_card(image_path):
    """Main function to parse Pokemon card and extract name and card number"""
    print("🎴 Pokemon Card Parser")
    print("=" * 50)
    
    # Get OCR text
    print("📖 Extracting text from image...")
    ocr_text = get_ocr_text(image_path)
    
    if not ocr_text:
        print("❌ No text could be extracted from the image")
        return None, None
    
    print(f"📝 OCR Text:\n{repr(ocr_text)}\n")
    
    # Extract card number
    print("🔢 Extracting card number...")
    card_info = extract_card_number(ocr_text)
    
    if card_info:
        print(f"✅ Card Number: {card_info['number']}")
        print(f"   Card #{card_info['card_num']} out of {card_info['total_cards']}")
    else:
        print("❌ No card number found")
    
    # Extract Pokemon name
    print("\n🐾 Extracting Pokemon name...")
    name_matches = extract_pokemon_name(ocr_text)
    
    pokemon_name = None
    if name_matches:
        # Always pick the first match (earliest in text)
        first_match = name_matches[0]
        pokemon_name = first_match['name']
        
        print(f"✅ Pokemon name found: {pokemon_name}")
        confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        emoji = confidence_emoji.get(first_match['confidence'], "⚪")
        print(f"   {emoji} Confidence: {first_match['confidence']}")
        print(f"   Match type: {first_match['match_type']}")
        if 'similarity' in first_match:
            print(f"   Similarity: {first_match['similarity']:.2f}, Matched text: '{first_match['matched_text']}'")
        if 'position' in first_match:
            print(f"   Position in text: {first_match['position']}")
        
        # Show other matches found (but not used)
        if len(name_matches) > 1:
            print(f"   Note: {len(name_matches)-1} other Pokemon name(s) found later in text (ignored)")
    else:
        print("❌ No Pokemon name found in predefined list")
    
    return pokemon_name, card_info

def main():
    # Example usage
    image_path = r"C:\Users\AlexF\Downloads\steelixcard.jpg"
    
    pokemon_name, card_info = parse_pokemon_card(image_path)
    
    print("\n" + "=" * 50)
    print("📋 FINAL RESULTS:")
    print("=" * 50)
    
    if pokemon_name:
        print(f"🐾 Pokemon: {pokemon_name}")
    else:
        print("🐾 Pokemon: Unknown")
    
    if card_info:
        print(f"🔢 Card: {card_info['number']}")
    else:
        print("🔢 Card: Unknown")

if __name__ == "__main__":
    main()


