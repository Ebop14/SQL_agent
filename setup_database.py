"""
Setup script to create a sample SQLite database with realistic data.
This creates a comprehensive e-commerce database with customers, products, orders,
reviews, suppliers, employees, and more.
"""

import sqlite3
from datetime import datetime, timedelta
import random
import hashlib

DB_PATH = "shop.db"

# Seed for reproducibility
random.seed(42)

# ============================================================================
# DATA GENERATORS
# ============================================================================

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
    "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane", "Aaron", "Ruth",
    "Jose", "Julie", "Adam", "Olivia", "Nathan", "Joyce", "Henry", "Virginia",
    "Douglas", "Victoria", "Zachary", "Kelly", "Peter", "Lauren", "Kyle", "Christina",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
    "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell",
]

CITIES = [
    ("New York", "NY", "10001", "USA"),
    ("Los Angeles", "CA", "90001", "USA"),
    ("Chicago", "IL", "60601", "USA"),
    ("Houston", "TX", "77001", "USA"),
    ("Phoenix", "AZ", "85001", "USA"),
    ("Philadelphia", "PA", "19101", "USA"),
    ("San Antonio", "TX", "78201", "USA"),
    ("San Diego", "CA", "92101", "USA"),
    ("Dallas", "TX", "75201", "USA"),
    ("San Jose", "CA", "95101", "USA"),
    ("Austin", "TX", "78701", "USA"),
    ("Jacksonville", "FL", "32099", "USA"),
    ("Fort Worth", "TX", "76101", "USA"),
    ("Columbus", "OH", "43085", "USA"),
    ("Charlotte", "NC", "28201", "USA"),
    ("San Francisco", "CA", "94102", "USA"),
    ("Indianapolis", "IN", "46201", "USA"),
    ("Seattle", "WA", "98101", "USA"),
    ("Denver", "CO", "80201", "USA"),
    ("Washington", "DC", "20001", "USA"),
    ("Boston", "MA", "02101", "USA"),
    ("Nashville", "TN", "37201", "USA"),
    ("Detroit", "MI", "48201", "USA"),
    ("Portland", "OR", "97201", "USA"),
    ("Las Vegas", "NV", "89101", "USA"),
    ("Memphis", "TN", "38101", "USA"),
    ("Louisville", "KY", "40201", "USA"),
    ("Baltimore", "MD", "21201", "USA"),
    ("Milwaukee", "WI", "53201", "USA"),
    ("Albuquerque", "NM", "87101", "USA"),
    ("Toronto", "ON", "M5A", "Canada"),
    ("Vancouver", "BC", "V5K", "Canada"),
    ("Montreal", "QC", "H1A", "Canada"),
    ("Calgary", "AB", "T1X", "Canada"),
    ("London", "ENG", "SW1A", "UK"),
    ("Manchester", "ENG", "M1", "UK"),
    ("Birmingham", "ENG", "B1", "UK"),
    ("Sydney", "NSW", "2000", "Australia"),
    ("Melbourne", "VIC", "3000", "Australia"),
    ("Brisbane", "QLD", "4000", "Australia"),
]

STREET_NAMES = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine St", "Elm Ave", "Washington Blvd",
    "Park Ave", "Lake Dr", "Hill Rd", "River Rd", "Forest Ave", "Sunset Blvd", "Broadway",
    "Highland Ave", "Valley Rd", "Church St", "School St", "Mill St", "Spring St",
    "Market St", "Union St", "Liberty Ave", "Franklin St", "Jefferson Ave", "Madison Ave",
    "Lincoln Way", "Monroe St", "Adams St", "Jackson Ave", "Harrison Blvd", "Tyler Ct",
]

CATEGORIES = [
    ("Electronics", "Electronic devices and accessories"),
    ("Furniture", "Home and office furniture"),
    ("Office Supplies", "Office and stationery items"),
    ("Clothing", "Apparel and fashion items"),
    ("Sports & Outdoors", "Sports equipment and outdoor gear"),
    ("Home & Kitchen", "Home goods and kitchen appliances"),
    ("Books", "Books, magazines, and publications"),
    ("Toys & Games", "Toys, games, and entertainment"),
    ("Health & Beauty", "Health, beauty, and personal care"),
    ("Automotive", "Car parts and accessories"),
    ("Garden & Patio", "Gardening tools and outdoor living"),
    ("Pet Supplies", "Pet food and accessories"),
]

PRODUCTS_BY_CATEGORY = {
    "Electronics": [
        ("Laptop Pro 15", "High-performance laptop with 15-inch display", 1299.99, "TechCorp", 2.1, 4.5),
        ("Laptop Air 13", "Lightweight laptop for everyday use", 899.99, "TechCorp", 1.3, 4.3),
        ("Gaming Laptop X", "Gaming laptop with RTX graphics", 1799.99, "GameTech", 2.8, 4.7),
        ("Budget Laptop", "Affordable laptop for basic tasks", 449.99, "ValueTech", 1.9, 3.9),
        ("Ultrabook Elite", "Premium ultrabook with OLED display", 1599.99, "TechCorp", 1.1, 4.6),
        ("Wireless Mouse", "Ergonomic wireless mouse", 29.99, "PeripheralCo", 0.1, 4.2),
        ("Gaming Mouse RGB", "High-DPI gaming mouse with RGB", 79.99, "GameTech", 0.15, 4.6),
        ("Vertical Mouse", "Ergonomic vertical mouse", 49.99, "PeripheralCo", 0.12, 4.1),
        ("Mechanical Keyboard", "Cherry MX mechanical keyboard", 129.99, "PeripheralCo", 0.9, 4.5),
        ("Gaming Keyboard RGB", "Mechanical gaming keyboard", 159.99, "GameTech", 1.0, 4.7),
        ("Wireless Keyboard", "Slim wireless keyboard", 59.99, "PeripheralCo", 0.5, 4.0),
        ("4K Monitor 27\"", "27-inch 4K IPS monitor", 449.99, "DisplayTech", 6.5, 4.4),
        ("Gaming Monitor 32\"", "32-inch 144Hz gaming monitor", 549.99, "DisplayTech", 8.2, 4.6),
        ("Ultrawide Monitor 34\"", "34-inch ultrawide curved monitor", 699.99, "DisplayTech", 9.1, 4.5),
        ("Portable Monitor 15\"", "15-inch portable USB-C monitor", 249.99, "DisplayTech", 1.2, 4.2),
        ("Wireless Headphones", "Over-ear noise-cancelling headphones", 249.99, "AudioMax", 0.25, 4.5),
        ("Gaming Headset", "7.1 surround sound gaming headset", 129.99, "GameTech", 0.35, 4.4),
        ("Earbuds Pro", "True wireless earbuds with ANC", 179.99, "AudioMax", 0.05, 4.3),
        ("Budget Earbuds", "Affordable wireless earbuds", 39.99, "AudioMax", 0.04, 3.8),
        ("Studio Headphones", "Professional studio monitor headphones", 199.99, "AudioMax", 0.3, 4.7),
        ("Webcam HD", "1080p HD webcam", 79.99, "TechCorp", 0.15, 4.1),
        ("Webcam 4K", "4K webcam with autofocus", 149.99, "TechCorp", 0.2, 4.4),
        ("USB Hub 7-Port", "Powered USB 3.0 hub", 39.99, "PeripheralCo", 0.2, 4.2),
        ("USB-C Dock", "Thunderbolt docking station", 199.99, "TechCorp", 0.4, 4.3),
        ("External SSD 1TB", "Portable SSD drive 1TB", 119.99, "StoragePro", 0.1, 4.6),
        ("External SSD 2TB", "Portable SSD drive 2TB", 199.99, "StoragePro", 0.12, 4.5),
        ("External HDD 4TB", "Portable hard drive 4TB", 99.99, "StoragePro", 0.25, 4.2),
        ("Smartphone Pro", "Flagship smartphone with 6.7\" display", 999.99, "MobileTech", 0.2, 4.5),
        ("Smartphone Lite", "Mid-range smartphone", 499.99, "MobileTech", 0.18, 4.2),
        ("Tablet Pro 12\"", "12.9-inch tablet with stylus support", 799.99, "TechCorp", 0.65, 4.6),
        ("Tablet Mini 8\"", "Compact 8-inch tablet", 399.99, "TechCorp", 0.3, 4.3),
        ("Smart Watch", "Fitness smartwatch with GPS", 299.99, "WearableTech", 0.05, 4.4),
        ("Fitness Band", "Basic fitness tracker", 49.99, "WearableTech", 0.03, 4.0),
        ("Bluetooth Speaker", "Portable Bluetooth speaker", 79.99, "AudioMax", 0.5, 4.3),
        ("Smart Speaker", "Voice-controlled smart speaker", 129.99, "HomeTech", 0.8, 4.2),
        ("Wireless Charger", "Fast wireless charging pad", 29.99, "PowerUp", 0.15, 4.1),
        ("Power Bank 20000mAh", "High-capacity portable charger", 49.99, "PowerUp", 0.4, 4.4),
        ("HDMI Cable 6ft", "High-speed HDMI 2.1 cable", 14.99, "CableCo", 0.1, 4.5),
        ("USB-C Cable 3-Pack", "Braided USB-C cables", 19.99, "CableCo", 0.08, 4.3),
    ],
    "Furniture": [
        ("Executive Desk Chair", "Ergonomic leather executive chair", 349.99, "OfficePro", 18.0, 4.4),
        ("Mesh Office Chair", "Breathable mesh ergonomic chair", 249.99, "OfficePro", 15.0, 4.5),
        ("Gaming Chair", "Racing-style gaming chair", 299.99, "GameTech", 22.0, 4.2),
        ("Standing Desk 60\"", "Electric standing desk 60-inch", 599.99, "DeskMaster", 45.0, 4.6),
        ("Standing Desk 48\"", "Electric standing desk 48-inch", 499.99, "DeskMaster", 38.0, 4.5),
        ("L-Shaped Desk", "Corner L-shaped computer desk", 299.99, "DeskMaster", 55.0, 4.3),
        ("Writing Desk", "Minimalist writing desk", 149.99, "HomeFurn", 25.0, 4.1),
        ("Bookshelf 5-Tier", "5-tier wooden bookshelf", 129.99, "HomeFurn", 30.0, 4.2),
        ("Filing Cabinet 3-Drawer", "Metal filing cabinet", 179.99, "OfficePro", 35.0, 4.0),
        ("Monitor Stand", "Adjustable monitor riser", 39.99, "DeskMaster", 2.5, 4.3),
        ("Desk Lamp LED", "Adjustable LED desk lamp", 49.99, "LightWorks", 1.2, 4.4),
        ("Floor Lamp", "Modern floor lamp", 89.99, "LightWorks", 4.5, 4.1),
        ("Sofa 3-Seater", "Modern 3-seater fabric sofa", 699.99, "HomeFurn", 65.0, 4.3),
        ("Armchair", "Comfortable accent armchair", 349.99, "HomeFurn", 28.0, 4.2),
        ("Coffee Table", "Glass top coffee table", 199.99, "HomeFurn", 20.0, 4.1),
        ("TV Stand 65\"", "TV stand for up to 65-inch TV", 249.99, "HomeFurn", 35.0, 4.2),
        ("Dining Table 6-Seat", "Wooden dining table for 6", 499.99, "HomeFurn", 50.0, 4.4),
        ("Dining Chair Set of 4", "Set of 4 dining chairs", 299.99, "HomeFurn", 25.0, 4.3),
        ("Bed Frame Queen", "Queen size platform bed frame", 399.99, "SleepWell", 60.0, 4.5),
        ("Nightstand", "2-drawer bedside nightstand", 99.99, "SleepWell", 15.0, 4.2),
    ],
    "Office Supplies": [
        ("Notebook 3-Pack", "College-ruled spiral notebooks", 9.99, "PaperCo", 0.5, 4.3),
        ("Legal Pad 12-Pack", "Yellow legal pads", 14.99, "PaperCo", 1.2, 4.4),
        ("Sticky Notes 12-Pack", "3x3 sticky notes assorted colors", 12.99, "PaperCo", 0.3, 4.5),
        ("Ballpoint Pens 50-Pack", "Black ballpoint pens", 9.99, "WriteCo", 0.4, 4.2),
        ("Gel Pens 24-Pack", "Colored gel pens", 14.99, "WriteCo", 0.3, 4.4),
        ("Mechanical Pencils 12-Pack", "0.7mm mechanical pencils", 11.99, "WriteCo", 0.2, 4.3),
        ("Highlighters 6-Pack", "Assorted color highlighters", 7.99, "WriteCo", 0.15, 4.4),
        ("Stapler Heavy Duty", "Heavy-duty desktop stapler", 24.99, "OfficePro", 0.8, 4.1),
        ("Staples 5000-Count", "Standard staples box", 5.99, "OfficePro", 0.3, 4.5),
        ("Paper Clips 500-Count", "Assorted size paper clips", 4.99, "OfficePro", 0.2, 4.3),
        ("Binder Clips 48-Pack", "Assorted binder clips", 8.99, "OfficePro", 0.4, 4.4),
        ("Scissors", "8-inch stainless steel scissors", 7.99, "OfficePro", 0.1, 4.2),
        ("Tape Dispenser", "Desktop tape dispenser with tape", 9.99, "OfficePro", 0.3, 4.1),
        ("Desk Organizer", "Mesh desk organizer set", 19.99, "OfficePro", 0.8, 4.3),
        ("Printer Paper Ream", "500 sheets letter size paper", 8.99, "PaperCo", 2.5, 4.5),
        ("Copy Paper Case", "10 reams copy paper", 49.99, "PaperCo", 25.0, 4.4),
        ("Envelopes #10 500-Count", "Business envelopes", 24.99, "PaperCo", 2.0, 4.2),
        ("Manila Folders 100-Pack", "Letter size manila folders", 19.99, "PaperCo", 3.0, 4.3),
        ("Hanging Folders 25-Pack", "Letter size hanging folders", 14.99, "PaperCo", 1.5, 4.4),
        ("Label Maker", "Handheld label maker", 39.99, "OfficePro", 0.4, 4.2),
        ("Calculator Scientific", "Scientific calculator", 19.99, "CalcTech", 0.2, 4.5),
        ("Calculator Desktop", "Large display desktop calculator", 14.99, "CalcTech", 0.3, 4.3),
        ("Whiteboard 36x24", "Magnetic dry-erase whiteboard", 49.99, "OfficePro", 5.0, 4.2),
        ("Whiteboard Markers 12-Pack", "Dry-erase markers assorted", 11.99, "WriteCo", 0.2, 4.4),
        ("Corkboard 24x18", "Cork bulletin board", 29.99, "OfficePro", 2.5, 4.1),
    ],
    "Clothing": [
        ("Men's T-Shirt Basic", "100% cotton basic t-shirt", 19.99, "BasicWear", 0.2, 4.2),
        ("Men's T-Shirt Premium", "Premium blend fitted t-shirt", 34.99, "FashionPlus", 0.25, 4.4),
        ("Men's Polo Shirt", "Classic polo shirt", 44.99, "FashionPlus", 0.3, 4.3),
        ("Men's Dress Shirt", "Button-down dress shirt", 59.99, "FormalWear", 0.35, 4.4),
        ("Men's Jeans Classic", "Classic fit denim jeans", 49.99, "DenimCo", 0.6, 4.3),
        ("Men's Jeans Slim", "Slim fit stretch jeans", 59.99, "DenimCo", 0.55, 4.4),
        ("Men's Chinos", "Classic chino pants", 54.99, "FashionPlus", 0.5, 4.2),
        ("Men's Hoodie", "Fleece pullover hoodie", 49.99, "BasicWear", 0.6, 4.4),
        ("Men's Jacket Denim", "Classic denim jacket", 79.99, "DenimCo", 0.9, 4.3),
        ("Men's Winter Coat", "Insulated winter parka", 149.99, "OutdoorGear", 1.8, 4.5),
        ("Women's T-Shirt Basic", "100% cotton basic t-shirt", 17.99, "BasicWear", 0.15, 4.2),
        ("Women's Blouse", "Elegant silk blouse", 54.99, "FashionPlus", 0.2, 4.4),
        ("Women's Dress Casual", "Casual day dress", 64.99, "FashionPlus", 0.3, 4.3),
        ("Women's Dress Formal", "Elegant evening dress", 129.99, "FormalWear", 0.4, 4.5),
        ("Women's Jeans Skinny", "Skinny fit stretch jeans", 54.99, "DenimCo", 0.5, 4.4),
        ("Women's Leggings", "High-waist athletic leggings", 39.99, "ActiveWear", 0.25, 4.5),
        ("Women's Cardigan", "Soft knit cardigan", 49.99, "BasicWear", 0.35, 4.3),
        ("Women's Winter Jacket", "Quilted winter jacket", 129.99, "OutdoorGear", 1.2, 4.4),
        ("Unisex Sneakers", "Classic canvas sneakers", 59.99, "FootGear", 0.8, 4.3),
        ("Running Shoes", "Performance running shoes", 119.99, "ActiveWear", 0.7, 4.6),
        ("Dress Shoes Men's", "Leather oxford shoes", 129.99, "FormalWear", 0.9, 4.4),
        ("Heels Women's", "Classic pump heels", 89.99, "FormalWear", 0.6, 4.2),
        ("Sandals", "Comfortable summer sandals", 39.99, "FootGear", 0.4, 4.1),
        ("Socks 6-Pack", "Athletic crew socks", 14.99, "BasicWear", 0.2, 4.3),
        ("Belt Leather", "Genuine leather belt", 34.99, "FashionPlus", 0.2, 4.4),
    ],
    "Sports & Outdoors": [
        ("Yoga Mat", "Non-slip yoga mat 6mm", 29.99, "FitGear", 1.2, 4.5),
        ("Yoga Block Set", "Foam yoga blocks 2-pack", 19.99, "FitGear", 0.4, 4.4),
        ("Resistance Bands Set", "5-level resistance bands", 24.99, "FitGear", 0.3, 4.5),
        ("Dumbbells 20lb Pair", "Rubber-coated dumbbells", 49.99, "IronWorks", 9.1, 4.6),
        ("Dumbbells 10lb Pair", "Rubber-coated dumbbells", 29.99, "IronWorks", 4.5, 4.5),
        ("Kettlebell 25lb", "Cast iron kettlebell", 44.99, "IronWorks", 11.3, 4.5),
        ("Jump Rope", "Speed jump rope", 14.99, "FitGear", 0.2, 4.3),
        ("Pull-Up Bar", "Doorway pull-up bar", 34.99, "FitGear", 2.5, 4.2),
        ("Exercise Ball 65cm", "Anti-burst exercise ball", 24.99, "FitGear", 1.0, 4.3),
        ("Foam Roller", "High-density foam roller", 29.99, "FitGear", 0.8, 4.5),
        ("Camping Tent 4-Person", "Waterproof dome tent", 149.99, "OutdoorGear", 6.0, 4.4),
        ("Sleeping Bag", "3-season sleeping bag", 79.99, "OutdoorGear", 2.5, 4.3),
        ("Camping Stove", "Portable propane stove", 49.99, "OutdoorGear", 1.5, 4.4),
        ("Cooler 48-Quart", "Hard-sided cooler", 89.99, "OutdoorGear", 8.0, 4.5),
        ("Hiking Backpack 40L", "Technical hiking backpack", 129.99, "OutdoorGear", 1.8, 4.6),
        ("Hiking Boots", "Waterproof hiking boots", 149.99, "OutdoorGear", 1.5, 4.5),
        ("Trekking Poles", "Adjustable trekking poles pair", 59.99, "OutdoorGear", 0.6, 4.4),
        ("Bicycle Helmet", "Adult cycling helmet", 49.99, "CycleGear", 0.4, 4.3),
        ("Bike Lock", "Heavy-duty U-lock", 39.99, "CycleGear", 1.2, 4.2),
        ("Water Bottle 32oz", "Insulated stainless steel bottle", 29.99, "HydroGear", 0.5, 4.6),
        ("Basketball", "Official size basketball", 29.99, "SportsBall", 0.6, 4.4),
        ("Soccer Ball", "Official size soccer ball", 24.99, "SportsBall", 0.4, 4.4),
        ("Tennis Racket", "Intermediate tennis racket", 79.99, "RacketPro", 0.3, 4.3),
        ("Golf Club Set", "Complete beginner golf set", 299.99, "GolfPro", 15.0, 4.2),
        ("Fishing Rod Combo", "Spinning rod and reel combo", 69.99, "AnglerGear", 0.8, 4.3),
    ],
    "Home & Kitchen": [
        ("Coffee Maker 12-Cup", "Programmable coffee maker", 79.99, "BrewMaster", 4.5, 4.4),
        ("Espresso Machine", "Semi-automatic espresso maker", 299.99, "BrewMaster", 8.0, 4.5),
        ("Electric Kettle", "1.7L stainless steel kettle", 39.99, "KitchenPro", 1.2, 4.5),
        ("Toaster 4-Slice", "Wide-slot toaster", 49.99, "KitchenPro", 2.0, 4.3),
        ("Blender", "High-power countertop blender", 99.99, "BlendTech", 5.0, 4.4),
        ("Food Processor", "12-cup food processor", 149.99, "KitchenPro", 7.5, 4.4),
        ("Stand Mixer", "Professional stand mixer", 349.99, "KitchenPro", 12.0, 4.7),
        ("Instant Pot 6-Quart", "Multi-use pressure cooker", 99.99, "InstaCook", 6.0, 4.6),
        ("Air Fryer 5.8-Quart", "Digital air fryer", 129.99, "CrispAir", 5.5, 4.5),
        ("Microwave 1.1 Cu Ft", "Countertop microwave", 119.99, "KitchenPro", 14.0, 4.2),
        ("Knife Set 15-Piece", "Stainless steel knife block set", 129.99, "ChefCraft", 6.0, 4.4),
        ("Cutting Board Set", "Bamboo cutting boards 3-pack", 34.99, "ChefCraft", 2.0, 4.5),
        ("Cookware Set 10-Piece", "Non-stick cookware set", 149.99, "CookWell", 15.0, 4.3),
        ("Cast Iron Skillet 12\"", "Pre-seasoned cast iron skillet", 44.99, "IronChef", 4.0, 4.7),
        ("Baking Sheet Set", "Non-stick baking sheets 3-pack", 29.99, "BakeWell", 2.5, 4.4),
        ("Mixing Bowls Set", "Stainless steel bowls 5-piece", 34.99, "ChefCraft", 3.0, 4.5),
        ("Storage Containers 24-Piece", "Airtight food storage set", 39.99, "FreshKeep", 2.0, 4.4),
        ("Dish Set 16-Piece", "Ceramic dinnerware set", 79.99, "TableWare", 12.0, 4.3),
        ("Flatware Set 20-Piece", "Stainless steel flatware", 49.99, "TableWare", 2.0, 4.4),
        ("Wine Glasses Set of 6", "Crystal wine glasses", 39.99, "GlassWorks", 1.5, 4.5),
        ("Robot Vacuum", "Smart robot vacuum cleaner", 299.99, "CleanTech", 6.0, 4.4),
        ("Vacuum Cordless", "Cordless stick vacuum", 249.99, "CleanTech", 5.5, 4.3),
        ("Air Purifier", "HEPA air purifier", 179.99, "PureAir", 8.0, 4.5),
        ("Humidifier", "Ultrasonic cool mist humidifier", 49.99, "PureAir", 2.5, 4.2),
        ("Iron Steam", "Steam iron with auto-off", 39.99, "PressWell", 2.0, 4.3),
    ],
    "Books": [
        ("Python Programming", "Learn Python programming basics", 39.99, "TechBooks", 0.8, 4.5),
        ("JavaScript Mastery", "Advanced JavaScript techniques", 44.99, "TechBooks", 0.9, 4.4),
        ("Data Science Handbook", "Complete guide to data science", 54.99, "TechBooks", 1.2, 4.6),
        ("Machine Learning Intro", "Introduction to ML algorithms", 49.99, "TechBooks", 1.0, 4.5),
        ("SQL Complete Guide", "Master SQL databases", 34.99, "TechBooks", 0.7, 4.4),
        ("Web Development", "Full-stack web development", 44.99, "TechBooks", 0.85, 4.3),
        ("Cloud Computing", "AWS and cloud fundamentals", 49.99, "TechBooks", 0.9, 4.4),
        ("Cybersecurity Basics", "Introduction to cybersecurity", 39.99, "TechBooks", 0.75, 4.3),
        ("The Great Novel", "Bestselling fiction novel", 16.99, "FictionHouse", 0.4, 4.2),
        ("Mystery Manor", "Thrilling mystery novel", 14.99, "FictionHouse", 0.35, 4.3),
        ("Romance in Paris", "Heartwarming romance", 13.99, "FictionHouse", 0.3, 4.1),
        ("Sci-Fi Adventures", "Science fiction anthology", 18.99, "FictionHouse", 0.45, 4.4),
        ("Fantasy Kingdom", "Epic fantasy series book 1", 17.99, "FictionHouse", 0.5, 4.6),
        ("History of Rome", "Comprehensive Roman history", 29.99, "AcademicPress", 0.9, 4.5),
        ("World War II", "Definitive WWII history", 34.99, "AcademicPress", 1.1, 4.6),
        ("Philosophy 101", "Introduction to philosophy", 24.99, "AcademicPress", 0.6, 4.2),
        ("Economics Explained", "Modern economics guide", 29.99, "AcademicPress", 0.7, 4.3),
        ("Cooking Masterclass", "Professional cooking techniques", 39.99, "LifestyleBooks", 1.5, 4.5),
        ("Healthy Eating", "Nutrition and meal planning", 24.99, "LifestyleBooks", 0.6, 4.3),
        ("Home Gardening", "Complete gardening guide", 29.99, "LifestyleBooks", 0.8, 4.4),
        ("DIY Home Repair", "Fix anything at home", 34.99, "LifestyleBooks", 1.0, 4.2),
        ("Mindfulness Guide", "Practice mindfulness daily", 19.99, "WellnessBooks", 0.4, 4.4),
        ("Fitness Revolution", "Transform your body", 24.99, "WellnessBooks", 0.5, 4.3),
        ("Children's Stories", "Illustrated children's book", 12.99, "KidsBooks", 0.5, 4.6),
        ("Coloring Book Adult", "Stress-relief coloring book", 9.99, "CreativeBooks", 0.4, 4.3),
    ],
    "Toys & Games": [
        ("Building Blocks 500pc", "Creative building blocks set", 29.99, "BlockWorld", 1.5, 4.6),
        ("Building Blocks 1000pc", "Large building blocks set", 49.99, "BlockWorld", 2.5, 4.7),
        ("Robot Building Kit", "STEM robot building kit", 79.99, "STEMToys", 1.0, 4.5),
        ("Science Kit Chemistry", "Kids chemistry experiment kit", 34.99, "STEMToys", 1.2, 4.4),
        ("Puzzle 1000 Pieces", "Landscape jigsaw puzzle", 19.99, "PuzzleCo", 0.8, 4.4),
        ("Puzzle 500 Pieces", "Animal jigsaw puzzle", 14.99, "PuzzleCo", 0.5, 4.3),
        ("Board Game Strategy", "Strategy board game for adults", 44.99, "GameNight", 1.5, 4.6),
        ("Board Game Family", "Family fun board game", 29.99, "GameNight", 1.0, 4.5),
        ("Card Game Party", "Party card game", 24.99, "GameNight", 0.3, 4.4),
        ("Chess Set Wood", "Wooden chess set", 39.99, "ClassicGames", 1.2, 4.5),
        ("Action Figure Hero", "Collectible action figure", 24.99, "ToyWorld", 0.3, 4.3),
        ("Doll Fashion", "Fashion doll with accessories", 29.99, "ToyWorld", 0.4, 4.4),
        ("RC Car Off-Road", "Remote control off-road car", 59.99, "RCWorld", 1.0, 4.3),
        ("Drone Mini", "Mini quadcopter drone", 49.99, "RCWorld", 0.3, 4.2),
        ("Plush Bear Large", "Large stuffed teddy bear", 34.99, "PlushPals", 0.8, 4.6),
        ("Plush Set Zoo", "Zoo animals plush set 5-piece", 44.99, "PlushPals", 1.0, 4.5),
        ("Play Kitchen", "Wooden play kitchen set", 129.99, "PretendPlay", 15.0, 4.4),
        ("Tool Set Kids", "Pretend tool set for kids", 29.99, "PretendPlay", 1.0, 4.3),
        ("Art Set Complete", "150-piece art supplies kit", 39.99, "ArtKids", 2.0, 4.5),
        ("Crayons 64-Pack", "Classic crayons with sharpener", 7.99, "ArtKids", 0.3, 4.6),
        ("Video Game Console", "Next-gen gaming console", 499.99, "GameTech", 4.5, 4.7),
        ("Video Game Adventure", "Adventure video game", 59.99, "GameTech", 0.1, 4.5),
        ("Video Game Sports", "Sports video game annual", 59.99, "GameTech", 0.1, 4.2),
        ("VR Headset", "Virtual reality headset", 299.99, "VRTech", 0.6, 4.4),
        ("Gaming Controller", "Wireless gaming controller", 69.99, "GameTech", 0.25, 4.5),
    ],
    "Health & Beauty": [
        ("Shampoo Hydrating", "Moisturizing shampoo 16oz", 12.99, "HairCare", 0.5, 4.3),
        ("Conditioner Repair", "Repairing conditioner 16oz", 14.99, "HairCare", 0.5, 4.4),
        ("Hair Dryer Pro", "Professional ionic hair dryer", 79.99, "HairCare", 0.9, 4.5),
        ("Flat Iron Ceramic", "Ceramic flat iron", 59.99, "HairCare", 0.4, 4.4),
        ("Face Moisturizer", "Daily face moisturizer SPF30", 24.99, "SkinGlow", 0.2, 4.5),
        ("Face Cleanser", "Gentle foaming cleanser", 18.99, "SkinGlow", 0.25, 4.4),
        ("Sunscreen SPF50", "Broad spectrum sunscreen", 14.99, "SkinGlow", 0.2, 4.5),
        ("Face Serum Vitamin C", "Brightening vitamin C serum", 34.99, "SkinGlow", 0.1, 4.6),
        ("Anti-Aging Cream", "Night repair cream", 49.99, "SkinGlow", 0.15, 4.4),
        ("Body Lotion", "Hydrating body lotion 16oz", 12.99, "BodyCare", 0.5, 4.3),
        ("Hand Cream", "Intensive hand repair cream", 9.99, "BodyCare", 0.1, 4.4),
        ("Lip Balm 3-Pack", "Moisturizing lip balms", 8.99, "BodyCare", 0.05, 4.5),
        ("Deodorant Natural", "Aluminum-free deodorant", 11.99, "BodyCare", 0.1, 4.2),
        ("Perfume Floral", "Floral eau de parfum 50ml", 79.99, "FragranceCo", 0.2, 4.4),
        ("Cologne Classic", "Classic cologne 100ml", 69.99, "FragranceCo", 0.25, 4.3),
        ("Electric Toothbrush", "Sonic electric toothbrush", 79.99, "DentalCare", 0.3, 4.6),
        ("Toothpaste Whitening", "Whitening toothpaste 2-pack", 9.99, "DentalCare", 0.3, 4.4),
        ("Floss Picks 150ct", "Dental floss picks", 6.99, "DentalCare", 0.1, 4.3),
        ("Mouthwash Mint", "Antiseptic mouthwash 1L", 8.99, "DentalCare", 1.0, 4.4),
        ("Multivitamin Daily", "Daily multivitamin 180ct", 24.99, "VitaHealth", 0.3, 4.4),
        ("Vitamin D 5000IU", "Vitamin D3 supplements 120ct", 14.99, "VitaHealth", 0.1, 4.5),
        ("Fish Oil 1000mg", "Omega-3 fish oil 200ct", 19.99, "VitaHealth", 0.4, 4.4),
        ("Protein Powder", "Whey protein 2lb", 34.99, "FitNutrition", 1.0, 4.5),
        ("First Aid Kit", "100-piece first aid kit", 24.99, "SafetyFirst", 0.8, 4.6),
        ("Blood Pressure Monitor", "Digital BP monitor", 49.99, "HealthMonitor", 0.4, 4.4),
    ],
    "Automotive": [
        ("Motor Oil 5W-30 5Qt", "Full synthetic motor oil", 29.99, "AutoLube", 4.5, 4.6),
        ("Motor Oil 10W-40 5Qt", "Conventional motor oil", 24.99, "AutoLube", 4.5, 4.4),
        ("Oil Filter", "Premium oil filter", 9.99, "FilterPro", 0.3, 4.5),
        ("Air Filter Engine", "Engine air filter", 19.99, "FilterPro", 0.2, 4.4),
        ("Cabin Air Filter", "Cabin air filter", 14.99, "FilterPro", 0.15, 4.3),
        ("Wiper Blades Pair", "All-season wiper blades", 24.99, "VisionClear", 0.4, 4.4),
        ("Car Battery", "12V automotive battery", 149.99, "PowerCell", 20.0, 4.3),
        ("Jumper Cables", "Heavy-duty jumper cables 20ft", 29.99, "AutoTools", 1.5, 4.5),
        ("Tire Inflator", "Portable tire inflator", 49.99, "AutoTools", 1.0, 4.4),
        ("Car Jack", "Hydraulic floor jack 2-ton", 79.99, "AutoTools", 15.0, 4.3),
        ("Tool Set Auto", "Mechanic tool set 200-piece", 129.99, "AutoTools", 12.0, 4.5),
        ("Car Cover", "Universal fit car cover", 49.99, "AutoShield", 3.0, 4.2),
        ("Floor Mats Set", "All-weather floor mats 4-piece", 39.99, "AutoShield", 2.5, 4.4),
        ("Seat Covers Pair", "Universal seat covers", 34.99, "AutoShield", 1.5, 4.1),
        ("Steering Wheel Cover", "Leather steering wheel cover", 19.99, "AutoShield", 0.3, 4.2),
        ("Car Phone Mount", "Magnetic phone mount", 19.99, "AutoTech", 0.2, 4.4),
        ("Dash Cam HD", "1080p dash camera", 79.99, "AutoTech", 0.2, 4.3),
        ("GPS Navigation", "Portable GPS navigator", 129.99, "AutoTech", 0.4, 4.2),
        ("Car Charger Dual USB", "Fast car charger", 14.99, "AutoTech", 0.1, 4.5),
        ("Bluetooth Car Adapter", "Bluetooth audio adapter", 24.99, "AutoTech", 0.1, 4.3),
        ("Car Wash Kit", "Complete car wash kit", 34.99, "DetailPro", 3.0, 4.4),
        ("Tire Shine", "Professional tire shine spray", 12.99, "DetailPro", 0.5, 4.3),
        ("Interior Cleaner", "Multi-surface interior cleaner", 9.99, "DetailPro", 0.6, 4.4),
        ("Headlight Restoration Kit", "Headlight restoration kit", 24.99, "DetailPro", 0.4, 4.2),
        ("Emergency Road Kit", "Roadside emergency kit", 59.99, "SafetyFirst", 5.0, 4.5),
    ],
    "Garden & Patio": [
        ("Garden Hose 50ft", "Heavy-duty garden hose", 34.99, "GardenPro", 3.5, 4.4),
        ("Hose Nozzle", "Adjustable spray nozzle", 14.99, "GardenPro", 0.3, 4.3),
        ("Sprinkler Oscillating", "Oscillating lawn sprinkler", 24.99, "GardenPro", 0.8, 4.2),
        ("Lawn Mower Electric", "Cordless electric mower", 299.99, "YardMaster", 35.0, 4.4),
        ("String Trimmer", "Cordless string trimmer", 129.99, "YardMaster", 4.0, 4.3),
        ("Leaf Blower", "Cordless leaf blower", 149.99, "YardMaster", 4.5, 4.4),
        ("Hedge Trimmer", "Electric hedge trimmer", 79.99, "YardMaster", 3.0, 4.3),
        ("Chainsaw Electric", "Electric chainsaw 16-inch", 149.99, "YardMaster", 8.0, 4.2),
        ("Garden Tool Set", "5-piece garden tool set", 29.99, "GardenPro", 2.0, 4.5),
        ("Pruning Shears", "Bypass pruning shears", 19.99, "GardenPro", 0.3, 4.6),
        ("Wheelbarrow", "Steel wheelbarrow 6 cu ft", 89.99, "GardenPro", 18.0, 4.3),
        ("Compost Bin", "Outdoor compost bin 80gal", 79.99, "GreenGrow", 6.0, 4.2),
        ("Potting Soil 40lb", "Premium potting soil", 14.99, "GreenGrow", 18.0, 4.5),
        ("Plant Food", "All-purpose plant fertilizer", 12.99, "GreenGrow", 2.0, 4.4),
        ("Seed Starter Kit", "72-cell seed starter tray", 19.99, "GreenGrow", 0.8, 4.3),
        ("Raised Garden Bed", "Cedar raised garden bed 4x4", 89.99, "GardenPro", 20.0, 4.5),
        ("Patio Umbrella 9ft", "Market patio umbrella", 79.99, "PatioLiving", 12.0, 4.3),
        ("Outdoor Chair Set 2", "Folding patio chairs 2-pack", 89.99, "PatioLiving", 14.0, 4.2),
        ("Patio Table", "Glass top patio table", 129.99, "PatioLiving", 25.0, 4.3),
        ("Outdoor Cushions Set", "Patio chair cushions 4-pack", 79.99, "PatioLiving", 4.0, 4.2),
        ("String Lights 50ft", "Outdoor string lights", 29.99, "PatioLiving", 1.0, 4.5),
        ("Solar Lights 8-Pack", "Solar pathway lights", 34.99, "PatioLiving", 2.0, 4.3),
        ("Fire Pit", "Wood-burning fire pit", 149.99, "PatioLiving", 25.0, 4.4),
        ("Grill Gas 3-Burner", "Propane gas grill", 299.99, "GrillMaster", 50.0, 4.5),
        ("Grill Charcoal", "Charcoal kettle grill", 149.99, "GrillMaster", 22.0, 4.6),
    ],
    "Pet Supplies": [
        ("Dog Food Dry 30lb", "Premium dry dog food", 49.99, "PetNutrition", 14.0, 4.5),
        ("Dog Food Wet 12-Pack", "Wet dog food cans", 29.99, "PetNutrition", 5.0, 4.4),
        ("Dog Treats Training", "Training treats 16oz", 12.99, "PetNutrition", 0.5, 4.5),
        ("Dog Treats Dental", "Dental chews 30-count", 24.99, "PetNutrition", 0.8, 4.4),
        ("Cat Food Dry 16lb", "Premium dry cat food", 39.99, "PetNutrition", 7.5, 4.5),
        ("Cat Food Wet 24-Pack", "Wet cat food variety", 24.99, "PetNutrition", 4.0, 4.4),
        ("Cat Treats", "Crunchy cat treats 10oz", 8.99, "PetNutrition", 0.3, 4.3),
        ("Dog Bed Large", "Orthopedic dog bed large", 59.99, "PetComfort", 5.0, 4.5),
        ("Dog Bed Medium", "Orthopedic dog bed medium", 44.99, "PetComfort", 3.5, 4.4),
        ("Cat Bed", "Cozy cat bed", 29.99, "PetComfort", 1.0, 4.3),
        ("Dog Crate Large", "Wire dog crate 42-inch", 79.99, "PetHome", 18.0, 4.4),
        ("Cat Tree", "Multi-level cat tree 72-inch", 99.99, "PetHome", 25.0, 4.5),
        ("Dog Collar Adjustable", "Adjustable nylon collar", 12.99, "PetGear", 0.1, 4.3),
        ("Dog Leash 6ft", "Nylon dog leash", 14.99, "PetGear", 0.2, 4.4),
        ("Dog Harness", "No-pull dog harness", 29.99, "PetGear", 0.3, 4.5),
        ("Cat Litter 40lb", "Clumping cat litter", 19.99, "CatCare", 18.0, 4.4),
        ("Litter Box Covered", "Covered litter box", 29.99, "CatCare", 3.0, 4.3),
        ("Litter Scoop", "Metal litter scoop", 9.99, "CatCare", 0.2, 4.4),
        ("Dog Toy Rope", "Durable rope toy", 9.99, "PetPlay", 0.3, 4.3),
        ("Dog Toy Ball Set", "Tennis balls 6-pack", 8.99, "PetPlay", 0.4, 4.5),
        ("Cat Toy Mouse Set", "Catnip mice 10-pack", 7.99, "PetPlay", 0.1, 4.4),
        ("Cat Toy Wand", "Interactive feather wand", 9.99, "PetPlay", 0.1, 4.5),
        ("Pet Carrier", "Soft-sided pet carrier", 39.99, "PetTravel", 2.0, 4.3),
        ("Dog Shampoo", "Gentle dog shampoo 16oz", 12.99, "PetGrooming", 0.5, 4.4),
        ("Pet Brush", "Deshedding brush", 19.99, "PetGrooming", 0.2, 4.5),
    ],
}

SUPPLIERS = [
    ("TechCorp Industries", "tech@techcorp.com", "555-0101", "100 Tech Park Dr", "San Jose", "CA", "USA"),
    ("GameTech Solutions", "sales@gametech.com", "555-0102", "200 Gaming Way", "Seattle", "WA", "USA"),
    ("PeripheralCo Ltd", "orders@peripheralco.com", "555-0103", "300 Peripheral Ave", "Austin", "TX", "USA"),
    ("DisplayTech Inc", "info@displaytech.com", "555-0104", "400 Monitor Blvd", "San Diego", "CA", "USA"),
    ("AudioMax Corp", "support@audiomax.com", "555-0105", "500 Sound St", "Nashville", "TN", "USA"),
    ("OfficePro Supply", "sales@officepro.com", "555-0106", "600 Office Plaza", "Chicago", "IL", "USA"),
    ("HomeFurn Direct", "orders@homefurn.com", "555-0107", "700 Furniture Lane", "Dallas", "TX", "USA"),
    ("FitGear Athletics", "info@fitgear.com", "555-0108", "800 Fitness Dr", "Denver", "CO", "USA"),
    ("PetNutrition Co", "sales@petnutrition.com", "555-0109", "900 Pet Way", "Portland", "OR", "USA"),
    ("GardenPro Supply", "orders@gardenpro.com", "555-0110", "1000 Garden Rd", "Phoenix", "AZ", "USA"),
]

DEPARTMENTS = [
    ("Sales", "Handles customer sales and account management"),
    ("Customer Support", "Provides customer service and technical support"),
    ("Warehouse", "Manages inventory and order fulfillment"),
    ("Marketing", "Handles advertising and promotions"),
    ("IT", "Manages technology infrastructure"),
    ("Finance", "Handles accounting and financial operations"),
    ("HR", "Manages human resources and recruitment"),
    ("Logistics", "Manages shipping and delivery"),
]

SHIPPING_METHODS = [
    ("Standard", 5.99, 5, 7),
    ("Express", 12.99, 2, 3),
    ("Overnight", 24.99, 1, 1),
    ("Economy", 3.99, 7, 14),
    ("Free Shipping", 0.00, 5, 10),
]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Apple Pay", "Google Pay", "Bank Transfer"]

DISCOUNT_CODES = [
    ("SAVE10", 10.0, "percentage", "2024-01-01", "2025-12-31", 100.0),
    ("SAVE20", 20.0, "percentage", "2024-01-01", "2025-12-31", 200.0),
    ("FLAT15", 15.0, "fixed", "2024-01-01", "2025-12-31", 75.0),
    ("FLAT25", 25.0, "fixed", "2024-01-01", "2025-12-31", 125.0),
    ("WELCOME5", 5.0, "percentage", "2024-01-01", "2025-12-31", 0.0),
    ("SUMMER15", 15.0, "percentage", "2024-06-01", "2024-08-31", 50.0),
    ("HOLIDAY20", 20.0, "percentage", "2024-11-01", "2024-12-31", 100.0),
    ("CLEARANCE30", 30.0, "percentage", "2024-01-01", "2025-12-31", 150.0),
]


def generate_phone():
    """Generate a random phone number."""
    return f"{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def generate_address():
    """Generate a random street address."""
    return f"{random.randint(1, 9999)} {random.choice(STREET_NAMES)}"


def setup_database():
    """Create and populate the sample database."""
    print("=" * 70)
    print("DATABASE SETUP - Large Scale")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Drop existing tables if they exist
    print("\n[STEP 1] Dropping existing tables (if any)...")
    tables_to_drop = [
        "reviews", "order_items", "orders", "inventory_log", "products",
        "customers", "employees", "suppliers", "categories", "shipping_methods",
        "discount_codes", "departments"
    ]
    for table in tables_to_drop:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    print("  ✓ Tables dropped")

    # Create tables
    print("\n[STEP 2] Creating tables...")

    # Categories table
    cursor.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            parent_category_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_category_id) REFERENCES categories(id)
        )
    """)
    print("  ✓ Created 'categories' table")

    # Suppliers table
    cursor.execute("""
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            rating REAL DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ Created 'suppliers' table")

    # Departments table
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            budget REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ Created 'departments' table")

    # Employees table
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            department_id INTEGER,
            manager_id INTEGER,
            hire_date TEXT,
            salary REAL,
            commission_pct REAL DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (manager_id) REFERENCES employees(id)
        )
    """)
    print("  ✓ Created 'employees' table")

    # Customers table (expanded)
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT DEFAULT 'USA',
            date_of_birth TEXT,
            gender TEXT,
            membership_tier TEXT DEFAULT 'Bronze',
            loyalty_points INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0,
            order_count INTEGER DEFAULT 0,
            preferred_payment TEXT,
            newsletter_subscribed INTEGER DEFAULT 0,
            account_status TEXT DEFAULT 'active',
            last_login TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ Created 'customers' table")

    # Products table (expanded)
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            brand TEXT,
            price REAL NOT NULL,
            cost REAL,
            weight REAL,
            stock INTEGER DEFAULT 0,
            reorder_level INTEGER DEFAULT 10,
            supplier_id INTEGER,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            is_featured INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    """)
    print("  ✓ Created 'products' table")

    # Shipping methods table
    cursor.execute("""
        CREATE TABLE shipping_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            min_days INTEGER,
            max_days INTEGER,
            is_active INTEGER DEFAULT 1
        )
    """)
    print("  ✓ Created 'shipping_methods' table")

    # Discount codes table
    cursor.execute("""
        CREATE TABLE discount_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            discount_value REAL NOT NULL,
            discount_type TEXT NOT NULL,
            valid_from TEXT,
            valid_until TEXT,
            minimum_order REAL DEFAULT 0,
            usage_count INTEGER DEFAULT 0,
            max_uses INTEGER,
            is_active INTEGER DEFAULT 1
        )
    """)
    print("  ✓ Created 'discount_codes' table")

    # Orders table (expanded)
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            employee_id INTEGER,
            order_date TEXT DEFAULT CURRENT_TIMESTAMP,
            required_date TEXT,
            shipped_date TEXT,
            status TEXT DEFAULT 'pending',
            shipping_method_id INTEGER,
            shipping_address TEXT,
            shipping_city TEXT,
            shipping_state TEXT,
            shipping_postal_code TEXT,
            shipping_country TEXT,
            subtotal REAL DEFAULT 0,
            shipping_cost REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pending',
            discount_code_id INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (shipping_method_id) REFERENCES shipping_methods(id),
            FOREIGN KEY (discount_code_id) REFERENCES discount_codes(id)
        )
    """)
    print("  ✓ Created 'orders' table")

    # Order items table (expanded)
    cursor.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount_pct REAL DEFAULT 0,
            line_total REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    print("  ✓ Created 'order_items' table")

    # Reviews table
    cursor.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            order_id INTEGER,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            title TEXT,
            comment TEXT,
            helpful_votes INTEGER DEFAULT 0,
            verified_purchase INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)
    print("  ✓ Created 'reviews' table")

    # Inventory log table
    cursor.execute("""
        CREATE TABLE inventory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            change_type TEXT NOT NULL,
            quantity_change INTEGER NOT NULL,
            quantity_after INTEGER NOT NULL,
            reference_type TEXT,
            reference_id INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    print("  ✓ Created 'inventory_log' table")

    # Insert sample data
    print("\n[STEP 3] Inserting sample data...")

    # Insert categories
    for name, desc in CATEGORIES:
        cursor.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (name, desc)
        )
    print(f"  ✓ Inserted {len(CATEGORIES)} categories")

    # Insert suppliers
    for supplier in SUPPLIERS:
        cursor.execute(
            """INSERT INTO suppliers (name, email, phone, address, city, state, country, rating)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (*supplier, round(random.uniform(3.5, 5.0), 1))
        )
    print(f"  ✓ Inserted {len(SUPPLIERS)} suppliers")

    # Insert departments
    for name, desc in DEPARTMENTS:
        budget = random.randint(50000, 500000)
        cursor.execute(
            "INSERT INTO departments (name, description, budget) VALUES (?, ?, ?)",
            (name, desc, budget)
        )
    print(f"  ✓ Inserted {len(DEPARTMENTS)} departments")

    # Insert employees (150 employees)
    num_employees = 150
    employees_data = []
    base_date = datetime.now() - timedelta(days=365 * 5)

    for i in range(num_employees):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@shop.com"
        phone = generate_phone()
        dept_id = random.randint(1, len(DEPARTMENTS))
        manager_id = random.randint(1, max(1, i)) if i > 10 else None
        hire_date = (base_date + timedelta(days=random.randint(0, 365 * 5))).strftime("%Y-%m-%d")
        salary = round(random.uniform(35000, 150000), 2)
        commission = round(random.uniform(0, 0.15), 2) if dept_id == 1 else 0

        employees_data.append((first_name, last_name, email, phone, dept_id, manager_id,
                               hire_date, salary, commission))

    cursor.executemany(
        """INSERT INTO employees (first_name, last_name, email, phone, department_id,
           manager_id, hire_date, salary, commission_pct) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        employees_data
    )
    print(f"  ✓ Inserted {num_employees} employees")

    # Insert shipping methods
    for method in SHIPPING_METHODS:
        cursor.execute(
            "INSERT INTO shipping_methods (name, price, min_days, max_days) VALUES (?, ?, ?, ?)",
            method
        )
    print(f"  ✓ Inserted {len(SHIPPING_METHODS)} shipping methods")

    # Insert discount codes
    for code in DISCOUNT_CODES:
        cursor.execute(
            """INSERT INTO discount_codes (code, discount_value, discount_type, valid_from,
               valid_until, minimum_order) VALUES (?, ?, ?, ?, ?, ?)""",
            code
        )
    print(f"  ✓ Inserted {len(DISCOUNT_CODES)} discount codes")

    # Insert customers (1000 customers)
    num_customers = 1000
    customers_data = []
    membership_tiers = ["Bronze", "Bronze", "Bronze", "Silver", "Silver", "Gold", "Platinum"]
    genders = ["Male", "Female", "Other", "Prefer not to say"]

    for i in range(num_customers):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        phone = generate_phone()
        city, state, postal, country = random.choice(CITIES)
        address = generate_address()
        dob = (datetime.now() - timedelta(days=random.randint(6570, 25550))).strftime("%Y-%m-%d")
        gender = random.choice(genders)
        tier = random.choice(membership_tiers)
        points = random.randint(0, 10000)
        payment = random.choice(PAYMENT_METHODS)
        newsletter = random.randint(0, 1)
        created = (datetime.now() - timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d %H:%M:%S")
        last_login = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")

        customers_data.append((first_name, last_name, email, phone, address, city, state,
                               postal, country, dob, gender, tier, points, payment,
                               newsletter, last_login, created))

    cursor.executemany(
        """INSERT INTO customers (first_name, last_name, email, phone, address, city, state,
           postal_code, country, date_of_birth, gender, membership_tier, loyalty_points,
           preferred_payment, newsletter_subscribed, last_login, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        customers_data
    )
    print(f"  ✓ Inserted {num_customers} customers")

    # Insert products
    products_data = []
    product_id = 0
    category_map = {cat[0]: i + 1 for i, cat in enumerate(CATEGORIES)}

    for category_name, products in PRODUCTS_BY_CATEGORY.items():
        category_id = category_map[category_name]
        for product in products:
            product_id += 1
            name, desc, price, brand, weight, rating = product
            sku = f"SKU-{category_id:02d}-{product_id:04d}"
            cost = round(price * random.uniform(0.4, 0.7), 2)
            stock = random.randint(0, 500)
            reorder = random.randint(5, 50)
            supplier_id = random.randint(1, len(SUPPLIERS))
            review_count = random.randint(0, 500)
            is_featured = 1 if random.random() < 0.1 else 0

            products_data.append((sku, name, desc, category_id, brand, price, cost, weight,
                                  stock, reorder, supplier_id, rating, review_count, is_featured))

    cursor.executemany(
        """INSERT INTO products (sku, name, description, category_id, brand, price, cost,
           weight, stock, reorder_level, supplier_id, rating, review_count, is_featured)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        products_data
    )
    num_products = len(products_data)
    print(f"  ✓ Inserted {num_products} products")

    # Insert orders (5000 orders over 2 years)
    num_orders = 5000
    orders_data = []
    base_date = datetime.now() - timedelta(days=730)
    statuses = ["pending", "processing", "shipped", "delivered", "delivered", "delivered", "delivered", "cancelled"]

    for i in range(num_orders):
        order_number = f"ORD-{100000 + i}"
        customer_id = random.randint(1, num_customers)
        employee_id = random.randint(1, num_employees) if random.random() > 0.3 else None
        order_date = (base_date + timedelta(days=random.randint(0, 730),
                                            hours=random.randint(0, 23),
                                            minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M:%S")
        status = random.choice(statuses)

        # Shipping info
        ship_method = random.randint(1, len(SHIPPING_METHODS))
        city, state, postal, country = random.choice(CITIES)
        ship_address = generate_address()

        # Payment
        payment_method = random.choice(PAYMENT_METHODS)
        payment_status = "completed" if status in ["shipped", "delivered"] else "pending"

        # Discount
        discount_id = random.randint(1, len(DISCOUNT_CODES)) if random.random() < 0.2 else None

        # Dates
        required_date = (datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S") +
                         timedelta(days=random.randint(3, 14))).strftime("%Y-%m-%d")
        shipped_date = None
        if status in ["shipped", "delivered"]:
            shipped_date = (datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S") +
                           timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d")

        orders_data.append((order_number, customer_id, employee_id, order_date, required_date,
                           shipped_date, status, ship_method, ship_address, city, state, postal,
                           country, payment_method, payment_status, discount_id))

    cursor.executemany(
        """INSERT INTO orders (order_number, customer_id, employee_id, order_date, required_date,
           shipped_date, status, shipping_method_id, shipping_address, shipping_city,
           shipping_state, shipping_postal_code, shipping_country, payment_method,
           payment_status, discount_code_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        orders_data
    )
    print(f"  ✓ Inserted {num_orders} orders")

    # Insert order items (average 2.5 items per order = ~12500 items)
    print("  ⏳ Generating order items...")
    order_items_data = []

    # Get product prices
    cursor.execute("SELECT id, price FROM products")
    product_prices = {row[0]: row[1] for row in cursor.fetchall()}

    for order_id in range(1, num_orders + 1):
        num_items = random.choices([1, 2, 3, 4, 5, 6], weights=[20, 35, 25, 12, 5, 3])[0]
        used_products = set()

        for _ in range(num_items):
            product_id = random.randint(1, num_products)
            while product_id in used_products:
                product_id = random.randint(1, num_products)
            used_products.add(product_id)

            quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 30, 12, 5, 3])[0]
            unit_price = product_prices[product_id]
            discount_pct = random.choice([0, 0, 0, 0, 0.05, 0.10, 0.15])
            line_total = round(quantity * unit_price * (1 - discount_pct), 2)

            order_items_data.append((order_id, product_id, quantity, unit_price, discount_pct, line_total))

    cursor.executemany(
        """INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct, line_total)
           VALUES (?, ?, ?, ?, ?, ?)""",
        order_items_data
    )
    print(f"  ✓ Inserted {len(order_items_data)} order items")

    # Update order totals
    print("  ⏳ Updating order totals...")
    cursor.execute("""
        UPDATE orders SET
            subtotal = (SELECT COALESCE(SUM(line_total), 0) FROM order_items WHERE order_items.order_id = orders.id),
            shipping_cost = (SELECT price FROM shipping_methods WHERE shipping_methods.id = orders.shipping_method_id),
            tax_amount = (SELECT COALESCE(SUM(line_total), 0) * 0.08 FROM order_items WHERE order_items.order_id = orders.id)
    """)
    cursor.execute("""
        UPDATE orders SET total_amount = subtotal + COALESCE(shipping_cost, 0) + tax_amount - discount_amount
    """)
    print("  ✓ Updated order totals")

    # Update customer stats
    print("  ⏳ Updating customer statistics...")
    cursor.execute("""
        UPDATE customers SET
            total_spent = (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE orders.customer_id = customers.id AND orders.status != 'cancelled'),
            order_count = (SELECT COUNT(*) FROM orders WHERE orders.customer_id = customers.id AND orders.status != 'cancelled')
    """)
    print("  ✓ Updated customer statistics")

    # Insert reviews (3000 reviews)
    print("  ⏳ Generating reviews...")
    num_reviews = 3000
    reviews_data = []
    review_titles = [
        "Great product!", "Exactly what I needed", "Good value", "Highly recommend",
        "Decent quality", "Not bad", "Could be better", "Disappointed",
        "Amazing!", "Perfect", "Works great", "Love it", "Excellent quality",
        "Good but pricey", "Okay product", "As described", "Fast shipping",
        "Exceeded expectations", "Will buy again", "Solid purchase"
    ]

    # Get delivered orders for verified purchases
    cursor.execute("""
        SELECT o.id, o.customer_id, oi.product_id
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.status = 'delivered'
    """)
    delivered_items = cursor.fetchall()

    for i in range(num_reviews):
        if delivered_items and random.random() < 0.7:
            # Verified purchase
            order_id, customer_id, product_id = random.choice(delivered_items)
            verified = 1
        else:
            # Non-verified
            product_id = random.randint(1, num_products)
            customer_id = random.randint(1, num_customers)
            order_id = None
            verified = 0

        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 8, 15, 35, 37])[0]
        title = random.choice(review_titles)
        comment = f"{'Great' if rating >= 4 else 'Decent' if rating == 3 else 'Poor'} product. " * random.randint(1, 3)
        helpful = random.randint(0, 50)
        created = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")

        reviews_data.append((product_id, customer_id, order_id, rating, title, comment, helpful, verified, created))

    cursor.executemany(
        """INSERT INTO reviews (product_id, customer_id, order_id, rating, title, comment,
           helpful_votes, verified_purchase, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        reviews_data
    )
    print(f"  ✓ Inserted {num_reviews} reviews")

    # Update product ratings based on reviews
    cursor.execute("""
        UPDATE products SET
            rating = COALESCE((SELECT AVG(rating) FROM reviews WHERE reviews.product_id = products.id), 0),
            review_count = (SELECT COUNT(*) FROM reviews WHERE reviews.product_id = products.id)
    """)
    print("  ✓ Updated product ratings")

    # Insert inventory logs
    print("  ⏳ Generating inventory logs...")
    inventory_logs = []
    for product_id in range(1, num_products + 1):
        # Initial stock
        cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        current_stock = cursor.fetchone()[0]

        # Generate some history
        num_entries = random.randint(5, 20)
        running_stock = current_stock + random.randint(100, 500)

        for j in range(num_entries):
            if random.random() < 0.4:
                # Sale
                change = -random.randint(1, 10)
                change_type = "sale"
            else:
                # Restock
                change = random.randint(20, 100)
                change_type = "restock"

            running_stock = max(0, running_stock + change)
            created = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")
            inventory_logs.append((product_id, change_type, change, running_stock, created))

    cursor.executemany(
        """INSERT INTO inventory_log (product_id, change_type, quantity_change, quantity_after, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        inventory_logs
    )
    print(f"  ✓ Inserted {len(inventory_logs)} inventory log entries")

    # Create indexes for better query performance
    print("\n[STEP 4] Creating indexes...")
    indexes = [
        "CREATE INDEX idx_customers_city ON customers(city)",
        "CREATE INDEX idx_customers_state ON customers(state)",
        "CREATE INDEX idx_customers_country ON customers(country)",
        "CREATE INDEX idx_customers_tier ON customers(membership_tier)",
        "CREATE INDEX idx_products_category ON products(category_id)",
        "CREATE INDEX idx_products_brand ON products(brand)",
        "CREATE INDEX idx_products_price ON products(price)",
        "CREATE INDEX idx_orders_customer ON orders(customer_id)",
        "CREATE INDEX idx_orders_date ON orders(order_date)",
        "CREATE INDEX idx_orders_status ON orders(status)",
        "CREATE INDEX idx_order_items_order ON order_items(order_id)",
        "CREATE INDEX idx_order_items_product ON order_items(product_id)",
        "CREATE INDEX idx_reviews_product ON reviews(product_id)",
        "CREATE INDEX idx_reviews_customer ON reviews(customer_id)",
        "CREATE INDEX idx_employees_dept ON employees(department_id)",
        "CREATE INDEX idx_inventory_product ON inventory_log(product_id)",
    ]
    for idx in indexes:
        cursor.execute(idx)
    print(f"  ✓ Created {len(indexes)} indexes")

    conn.commit()
    conn.close()

    # Print summary
    print("\n" + "=" * 70)
    print("DATABASE SETUP COMPLETE")
    print("=" * 70)
    print(f"\nDatabase file: {DB_PATH}")
    print("\nTable summary:")
    print(f"  • categories:      {len(CATEGORIES):,} rows")
    print(f"  • suppliers:       {len(SUPPLIERS):,} rows")
    print(f"  • departments:     {len(DEPARTMENTS):,} rows")
    print(f"  • employees:       {num_employees:,} rows")
    print(f"  • customers:       {num_customers:,} rows")
    print(f"  • products:        {num_products:,} rows")
    print(f"  • shipping_methods:{len(SHIPPING_METHODS):,} rows")
    print(f"  • discount_codes:  {len(DISCOUNT_CODES):,} rows")
    print(f"  • orders:          {num_orders:,} rows")
    print(f"  • order_items:     {len(order_items_data):,} rows")
    print(f"  • reviews:         {num_reviews:,} rows")
    print(f"  • inventory_log:   {len(inventory_logs):,} rows")
    print(f"\n  TOTAL:             {len(CATEGORIES) + len(SUPPLIERS) + len(DEPARTMENTS) + num_employees + num_customers + num_products + len(SHIPPING_METHODS) + len(DISCOUNT_CODES) + num_orders + len(order_items_data) + num_reviews + len(inventory_logs):,} rows")
    print("=" * 70)


if __name__ == "__main__":
    setup_database()
