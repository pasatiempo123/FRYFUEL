"""FRY FUEL business data.

Edit this file to change prices, products, promo codes, or store hours.
main.py imports everything from here.
"""

CURRENCY = "₱"          # change to "$" etc. if needed
DELIVERY_FEE = 30
OPEN_HOUR = 10          # 10:00 am
CLOSE_HOUR = 22         # 10:00 pm

# promo code -> discount rate
PROMOS = {
    "FUEL10": 0.10,
    "FIRSTBOX": 0.15,
}

MENU = [
    {"id": "classic", "name": "Classic Salted", "category": "Classics", "price": 79, "emoji": "🍟",
     "desc": "Golden, crispy, and salted the moment it leaves the oil.", "tag": "Best seller"},
    {"id": "cheese", "name": "Cheese Blast", "category": "Classics", "price": 99, "emoji": "🧀",
     "desc": "Tossed in sharp cheddar powder. Messy fingers guaranteed.", "tag": ""},
    {"id": "garlic", "name": "Garlic Parmesan", "category": "Classics", "price": 119, "emoji": "🧄",
     "desc": "Roasted garlic butter, parmesan, and fresh parsley.", "tag": ""},
    {"id": "cajun", "name": "Spicy Cajun", "category": "Classics", "price": 99, "emoji": "🌶️",
     "desc": "Smoky paprika and cayenne with a slow, warm kick.", "tag": "Hot"},
    {"id": "chili", "name": "Chili Cheese Loaded", "category": "Loaded", "price": 169, "emoji": "🔥",
     "desc": "Fries under beef chili, melted cheese, and jalapeños.", "tag": ""},
    {"id": "bacon", "name": "Bacon Ranch Loaded", "category": "Loaded", "price": 179, "emoji": "🥓",
     "desc": "Crispy bacon bits, cool ranch, and spring onion.", "tag": ""},
    {"id": "supreme", "name": "Fuel Supreme", "category": "Loaded", "price": 199, "emoji": "⚡",
     "desc": "Our biggest box: cheese, bacon, chili, and a sunny egg.", "tag": "Biggest box"},
    {"id": "tea", "name": "Iced Tea", "category": "Drinks", "price": 49, "emoji": "🧊",
     "desc": "Fresh-brewed and lightly sweet.", "tag": ""},
    {"id": "cola", "name": "Cola", "category": "Drinks", "price": 45, "emoji": "🥤",
     "desc": "Ice-cold, 16 oz cup.", "tag": ""},
]
