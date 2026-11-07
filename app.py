import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "nestcraft_secret_2026")

# ৫০টি আলাদা ডিজাইনের ইউনিক ফার্নিচার তালিকা
INITIAL_PRODUCTS = [
    # Living Room (1-12)
    {"id": 1, "name": "Nordic Oak 3-Seater Sofa", "category": "Living Room", "price": 48500, "material": "Solid Teak & Linen", "dimensions": "210 x 85 x 80 cm", "warranty": "5 Years", "badge": "Best Seller", "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80", "description": "Handcrafted Scandinavian style sofa with plush high-density foam cushions and kiln-dried solid teak legs."},
    {"id": 2, "name": "Velvet Chesterfield Lounge Chair", "category": "Living Room", "price": 22900, "material": "Emerald Velvet & Mahogany", "dimensions": "95 x 85 x 78 cm", "warranty": "3 Years", "badge": "Luxury", "image": "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&w=800&q=80", "description": "Deep button-tufted luxury armchair designed for statement living spaces and cozy reading corners."},
    {"id": 3, "name": "Mid-Century Walnut Coffee Table", "category": "Living Room", "price": 14500, "material": "American Walnut Veneer", "dimensions": "120 x 60 x 45 cm", "warranty": "3 Years", "badge": "New", "image": "https://images.unsplash.com/photo-1532372320572-cda25653a26d?auto=format&fit=crop&w=800&q=80", "description": "Sleek low-profile center table featuring hidden storage drawers and angled tapered legs."},
    {"id": 4, "name": "Artisan Rattan Accent Chair", "category": "Living Room", "price": 16800, "material": "Natural Cane & Ash Wood", "dimensions": "70 x 72 x 76 cm", "warranty": "2 Years", "badge": "Eco", "image": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?auto=format&fit=crop&w=800&q=80", "description": "Breathable hand-woven cane backrest paired with ergonomic solid ash wood framing."},
    {"id": 5, "name": "Minimalist Floating TV Console", "category": "Living Room", "price": 19200, "material": "Matte Oak & Steel", "dimensions": "180 x 40 x 35 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80", "description": "Wall-mounted media unit with concealed cable management and soft-close cabinets."},
    {"id": 6, "name": "Modular L-Shape Sectional Sofa", "category": "Living Room", "price": 74000, "material": "Performance Weave & Pine", "dimensions": "280 x 175 x 82 cm", "warranty": "5 Years", "badge": "Premium", "image": "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=800&q=80", "description": "Spacious family sectional with reversible chaise and stain-resistant woven upholstery."},
    {"id": 7, "name": "Marble Top Nesting Side Tables", "category": "Living Room", "price": 12500, "material": "Carrara Marble & Brass", "dimensions": "50 x 50 x 55 cm", "warranty": "2 Years", "badge": "", "image": "https://images.unsplash.com/photo-1533090481720-856c6e3c1fdc?auto=format&fit=crop&w=800&q=80", "description": "Set of two overlapping accent tables with genuine white marble tops and brushed gold frames."},
    {"id": 8, "name": "Industrial Bookshelf Divider", "category": "Living Room", "price": 24000, "material": "Reclaimed Teak & Iron", "dimensions": "150 x 35 x 185 cm", "warranty": "5 Years", "badge": "Trending", "image": "https://images.unsplash.com/photo-1594620302200-9a762244a156?auto=format&fit=crop&w=800&q=80", "description": "Open-back architectural shelving unit ideal for displaying books, ceramics, and indoor plants."},
    {"id": 9, "name": "Boucle Cloud Swivel Chair", "category": "Living Room", "price": 27500, "material": "Ivory Boucle & Steel Base", "dimensions": "85 x 82 x 74 cm", "warranty": "3 Years", "badge": "Hot", "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80", "description": "360-degree swivel lounge chair upholstered in ultra-soft textured ivory boucle fabric."},
    {"id": 10, "name": "Heritage Carved Wooden Diwan", "category": "Living Room", "price": 32000, "material": "Chittagong Teak Wood", "dimensions": "195 x 75 x 70 cm", "warranty": "10 Years", "badge": "Heritage", "image": "https://images.unsplash.com/photo-1540574163026-643ea20ade25?auto=format&fit=crop&w=800&q=80", "description": "Traditional Bengali craftsmanship blended with contemporary minimalist bolsters."},
    {"id": 11, "name": "Glass & Oak Display Cabinet", "category": "Living Room", "price": 36500, "material": "Tempered Glass & White Oak", "dimensions": "100 x 42 x 175 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=800&q=80", "description": "Fluted glass double-door curio cabinet with warm integrated LED shelf lighting."},
    {"id": 12, "name": "Leather Ottoman Pouf", "category": "Living Room", "price": 9800, "material": "Full-Grain Tan Leather", "dimensions": "60 x 60 x 42 cm", "warranty": "2 Years", "badge": "", "image": "https://images.unsplash.com/photo-1519947486511-46149fa0a254?auto=format&fit=crop&w=800&q=80", "description": "Hand-stitched genuine leather footrest that doubles as extra seating for guests."},

    # Bedroom (13-24)
    {"id": 13, "name": "Sovereign King Platform Bed", "category": "Bedroom", "price": 58000, "material": "Solid Burma Teak", "dimensions": "215 x 190 x 110 cm", "warranty": "10 Years", "badge": "Best Seller", "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80", "description": "Low-profile solid wood bed frame with slatted orthopedic mattress support and angled headboard."},
    {"id": 14, "name": "Upholstered Wingback Queen Bed", "category": "Bedroom", "price": 49500, "material": "Charcoal Fabric & Oak", "dimensions": "210 x 165 x 125 cm", "warranty": "5 Years", "badge": "", "image": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?auto=format&fit=crop&w=800&q=80", "description": "Tall padded wingback headboard offering supreme comfort for late-night reading."},
    {"id": 15, "name": "Nordic 2-Drawer Nightstand", "category": "Bedroom", "price": 9500, "material": "Natural Ash Wood", "dimensions": "50 x 40 x 52 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1532372576444-dda954194ad0?auto=format&fit=crop&w=800&q=80", "description": "Compact bedside table with smooth-glide drawers and carved finger-pull handles."},
    {"id": 16, "name": "Sliding Mirror 3-Door Wardrobe", "category": "Bedroom", "price": 68000, "material": "Engineered Oak & Mirror", "dimensions": "220 x 60 x 210 cm", "warranty": "5 Years", "badge": "Popular", "image": "https://images.unsplash.com/photo-1558997519-83ea9252edf8?auto=format&fit=crop&w=800&q=80", "description": "Space-saving sliding wardrobe featuring full-length mirror, hanging rails, and lockable safe."},
    {"id": 17, "name": "6-Drawer Wide Chest Dresser", "category": "Bedroom", "price": 34500, "material": "Solid Mahogany Wood", "dimensions": "140 x 48 x 85 cm", "warranty": "5 Years", "badge": "", "image": "https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?auto=format&fit=crop&w=800&q=80", "description": "Deep-drawer clothing organizer with dovetail joinery and matte black brass knobs."},
    {"id": 18, "name": "Vanity Dressing Table with Stool", "category": "Bedroom", "price": 26800, "material": "White Oak & Beveled Glass", "dimensions": "105 x 45 x 145 cm", "warranty": "3 Years", "badge": "New", "image": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=800&q=80", "description": "Elegant makeup vanity with round illuminated mirror, jewelry organizer tray, and cushioned stool."},
    {"id": 19, "name": "Canopy Four-Poster Bed Frame", "category": "Bedroom", "price": 72000, "material": "Matte Black Teak", "dimensions": "215 x 185 x 205 cm", "warranty": "10 Years", "badge": "Luxury", "image": "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?auto=format&fit=crop&w=800&q=80", "description": "Architectural four-poster statement bed crafted for spacious master bedrooms."},
    {"id": 20, "name": "Bedroom End-of-Bed Bench", "category": "Bedroom", "price": 13200, "material": "Linen & Walnut Legs", "dimensions": "130 x 45 x 48 cm", "warranty": "2 Years", "badge": "", "image": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=800&q=80", "description": "Tufted bench ideal for placing at the foot of the bed or in entryways."},
    {"id": 21, "name": "Floating Bedside Wall Shelf", "category": "Bedroom", "price": 5400, "material": "Solid Teak Wood", "dimensions": "45 x 30 x 18 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "description": "Minimalist wall-mounted nightstand for compact modern apartments."},
    {"id": 22, "name": "Woven Cane Headboard Queen", "category": "Bedroom", "price": 41000, "material": "Rattan & Teak Frame", "dimensions": "208 x 162 x 115 cm", "warranty": "5 Years", "badge": "", "image": "https://images.unsplash.com/photo-1617325247661-675ab4b64ae2?auto=format&fit=crop&w=800&q=80", "description": "Tropical modern bed frame combining warm wood tones with airy handwoven cane."},
    {"id": 23, "name": "Tallboy 5-Drawer Lingerie Chest", "category": "Bedroom", "price": 23500, "material": "Smoked Oak Finish", "dimensions": "65 x 45 x 125 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=800&q=80", "description": "Vertical storage tower that maximizes floor space in cozy bedrooms."},
    {"id": 24, "name": "Full-Length Standing Floor Mirror", "category": "Bedroom", "price": 11800, "material": "Arched Brass & Oak", "dimensions": "65 x 5 x 175 cm", "warranty": "2 Years", "badge": "Trending", "image": "https://images.unsplash.com/photo-1618220179428-22790b461013?auto=format&fit=crop&w=800&q=80", "description": "Oversized arched dressing mirror with sturdy foldable easel stand."},

    # Dining (25-34)
    {"id": 25, "name": "6-Seater Live-Edge Dining Set", "category": "Dining", "price": 64000, "material": "Acacia Wood & Steel", "dimensions": "180 x 90 x 76 cm", "warranty": "10 Years", "badge": "Best Seller", "image": "https://images.unsplash.com/photo-1617806118233-18e1de247200?auto=format&fit=crop&w=800&q=80", "description": "Natural organic live-edge dining table accompanied by 6 ergonomic cushioned chairs."},
    {"id": 26, "name": "Round Pedestal Marble Dining Table", "category": "Dining", "price": 52000, "material": "Italian Marble & Teak", "dimensions": "130 x 130 x 76 cm", "warranty": "5 Years", "badge": "Luxury", "image": "https://images.unsplash.com/photo-1577140917170-285929fb55b7?auto=format&fit=crop&w=800&q=80", "description": "4-to-6 seater circular dining table with fluted wooden pedestal base."},
    {"id": 27, "name": "Wishbone Woven Dining Chair (Pair)", "category": "Dining", "price": 15600, "material": "Solid Beech & Paper Cord", "dimensions": "55 x 51 x 76 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=800&q=80", "description": "Iconic Danish Y-back dining chairs hand-strung with durable natural paper cord."},
    {"id": 28, "name": "Buffet Sideboard Credenza", "category": "Dining", "price": 38500, "material": "Walnut & Brushed Brass", "dimensions": "160 x 45 x 82 cm", "warranty": "5 Years", "badge": "", "image": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=800&q=80", "description": "Spacious crockery and cutlery cabinet with adjustable shelves and wine rack."},
    {"id": 29, "name": "8-Seater Royal Teak Banquet Table", "category": "Dining", "price": 85000, "material": "Seasoned Chittagong Teak", "dimensions": "240 x 105 x 76 cm", "warranty": "15 Years", "badge": "Royal", "image": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=800&q=80", "description": "Grand family dining table engineered to last generations with rich satin lacquer."},
    {"id": 30, "name": "Counter Height Bar Stool (Set of 2)", "category": "Dining", "price": 14200, "material": "Faux Leather & Matte Iron", "dimensions": "45 x 48 x 95 cm", "warranty": "2 Years", "badge": "", "image": "https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=800&q=80", "description": "Modern kitchen island stools with built-in footrests and contoured backrests."},
    {"id": 31, "name": "Rolling Kitchen Bar Cart", "category": "Dining", "price": 11500, "material": "Tempered Glass & Gold Steel", "dimensions": "80 x 40 x 85 cm", "warranty": "2 Years", "badge": "New", "image": "https://images.unsplash.com/photo-1533090481720-856c6e3c1fdc?auto=format&fit=crop&w=800&q=80", "description": "Mobile serving trolley with lockable caster wheels and stemware holders."},
    {"id": 32, "name": "Extendable Oak Dining Table", "category": "Dining", "price": 46000, "material": "European White Oak", "dimensions": "140-200 x 90 x 76 cm", "warranty": "5 Years", "badge": "Smart", "image": "https://images.unsplash.com/photo-1617806118233-18e1de247200?auto=format&fit=crop&w=800&q=80", "description": "Butterfly leaf extension mechanism effortlessly expands from 4 to 8 seats."},
    {"id": 33, "name": "Solid Wood Dining Bench", "category": "Dining", "price": 12800, "material": "Solid Acacia Wood", "dimensions": "150 x 38 x 45 cm", "warranty": "5 Years", "badge": "", "image": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=800&q=80", "description": "Versatile backless dining bench that tucks neatly underneath the table."},
    {"id": 34, "name": "Compact 2-Seater Bistro Set", "category": "Dining", "price": 18900, "material": "Teak & Powder-Coated Steel", "dimensions": "75 x 75 x 75 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1577140917170-285929fb55b7?auto=format&fit=crop&w=800&q=80", "description": "Ideal breakfast nook or balcony dining set for cozy urban apartments."},

    # Office (35-42)
    {"id": 35, "name": "Executive L-Shape Manager Desk", "category": "Office", "price": 42000, "material": "Walnut & Matte Steel", "dimensions": "180 x 150 x 75 cm", "warranty": "5 Years", "badge": "Executive", "image": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?auto=format&fit=crop&w=800&q=80", "description": "Commanding corner workstation with built-in file pedestal and wire grommets."},
    {"id": 36, "name": "Ergonomic Mesh Pro Task Chair", "category": "Office", "price": 18500, "material": "Breathable Mesh & Nylon", "dimensions": "66 x 64 x 118 cm", "warranty": "3 Years", "badge": "Best Seller", "image": "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?auto=format&fit=crop&w=800&q=80", "description": "Adjustable lumbar support, 3D armrests, and synchro-tilt mechanism for 10+ hour comfort."},
    {"id": 37, "name": "Motorized Standing Desk", "category": "Office", "price": 39500, "material": "Bamboo Top & Dual Motor", "dimensions": "150 x 75 x 72-120 cm", "warranty": "5 Years", "badge": "Smart", "image": "https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?auto=format&fit=crop&w=800&q=80", "description": "Electric height-adjustable desk with 4 memory presets and anti-collision sensor."},
    {"id": 38, "name": "Minimalist Home Study Table", "category": "Office", "price": 14800, "material": "Solid Oak Wood", "dimensions": "120 x 60 x 75 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?auto=format&fit=crop&w=800&q=80", "description": "Clean Scandinavian writing desk with two slim stationery drawers."},
    {"id": 39, "name": "High-Back Leather Director Chair", "category": "Office", "price": 26500, "material": "Top-Grain Leather & Chrome", "dimensions": "70 x 68 x 122 cm", "warranty": "3 Years", "badge": "Luxury", "image": "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?auto=format&fit=crop&w=800&q=80", "description": "Ribbed executive swivel chair with heavy-duty aluminum base and tilt lock."},
    {"id": 40, "name": "Lockable 3-Drawer Mobile Pedestal", "category": "Office", "price": 8900, "material": "Cold-Rolled Steel", "dimensions": "40 x 50 x 60 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1594620302200-9a762244a156?auto=format&fit=crop&w=800&q=80", "description": "Under-desk rolling file cabinet with central locking system for confidential documents."},
    {"id": 41, "name": "8-Person Conference Boardroom Table", "category": "Office", "price": 78000, "material": "Teak Veneer & Aluminum", "dimensions": "260 x 120 x 76 cm", "warranty": "5 Years", "badge": "Corporate", "image": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=800&q=80", "description": "Modern meeting table equipped with integrated power and HDMI connectivity box."},
    {"id": 42, "name": "Ladder Wall Leaning Bookshelf", "category": "Office", "price": 11200, "material": "Solid Ash Wood", "dimensions": "75 x 38 x 180 cm", "warranty": "2 Years", "badge": "", "image": "https://images.unsplash.com/photo-1594620302200-9a762244a156?auto=format&fit=crop&w=800&q=80", "description": "5-tier angled studio shelf for organizing binders, books, and office decor."},

    # Decor (43-50)
    {"id": 43, "name": "Tripod Mid-Century Floor Lamp", "category": "Decor", "price": 7800, "material": "Teak Legs & Linen Shade", "dimensions": "50 x 50 x 155 cm", "warranty": "1 Year", "badge": "Popular", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80", "description": "Warm ambient standing lamp that casts a soft glow across living rooms."},
    {"id": 44, "name": "Hand-Tufted Wool Area Rug (5x8 ft)", "category": "Decor", "price": 13500, "material": "100% New Zealand Wool", "dimensions": "240 x 150 cm", "warranty": "2 Years", "badge": "Artisan", "image": "https://images.unsplash.com/photo-1575414003591-ece8d0416c7a?auto=format&fit=crop&w=800&q=80", "description": "Geometric minimalist carpet woven by master artisans for plush underfoot warmth."},
    {"id": 45, "name": "Ceramic Vase Trio Set", "category": "Decor", "price": 3600, "material": "Matte Stoneware Clay", "dimensions": "15 x 15 x 30 cm", "warranty": "N/A", "badge": "Gift Idea", "image": "https://images.unsplash.com/photo-1581783898377-1c85bf937427?auto=format&fit=crop&w=800&q=80", "description": "Set of three textured earth-tone vases for pampas grass or fresh florals."},
    {"id": 46, "name": "Abstract Framed Canvas Wall Art", "category": "Decor", "price": 6200, "material": "Cotton Canvas & Oak Frame", "dimensions": "90 x 120 cm", "warranty": "N/A", "badge": "New", "image": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=800&q=80", "description": "Hand-painted minimalist textured artwork framed in natural solid oak."},
    {"id": 47, "name": "Teak Wood Indoor Plant Stand", "category": "Decor", "price": 4200, "material": "Burma Teak Wood", "dimensions": "35 x 35 x 65 cm", "warranty": "2 Years", "badge": "", "image": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80", "description": "Elevated mid-century planter holder suitable for 10-to-12 inch ceramic pots."},
    {"id": 48, "name": "Brass & Marble Table Lamp", "category": "Decor", "price": 5500, "material": "Green Marble & Brushed Gold", "dimensions": "25 x 25 x 45 cm", "warranty": "1 Year", "badge": "", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80", "description": "Luxury bedside or desk lamp with dimmable warm LED bulb included."},
    {"id": 49, "name": "Wall-Mounted Coat & Hat Rack", "category": "Decor", "price": 3200, "material": "Walnut & Brass Hooks", "dimensions": "70 x 10 x 15 cm", "warranty": "3 Years", "badge": "", "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "description": "Entryway organizer featuring 5 retractable heavy-duty brass hooks."},
    {"id": 50, "name": "Silent Wooden Pendulum Wall Clock", "category": "Decor", "price": 4800, "material": "Solid Walnut & Brass", "dimensions": "35 x 5 x 55 cm", "warranty": "2 Years", "badge": "Classic", "image": "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?auto=format&fit=crop&w=800&q=80", "description": "Non-ticking sweep movement timepiece crafted from rich walnut wood."}
]

# MongoDB Atlas Safe Connection (কানেকশন এরর হলেও সাইট ক্র্যাশ করবে না)
MONGO_URI = os.getenv("MONGO_URI", "").strip()
db_connected = False
products_col = None
orders_col = None
messages_col = None
local_orders = []
local_messages = []

if MONGO_URI and "xxxxx" not in MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client["nestcraft_store"]
        products_col = db["products"]
        orders_col = db["orders"]
        messages_col = db["messages"]
        if products_col.count_documents({}) == 0:
            products_col.insert_many(INITIAL_PRODUCTS)
        db_connected = True
        print("SUCCESS: Connected to MongoDB Atlas!")
    except Exception as e:
        print(f"WARNING: MongoDB Atlas not connected ({e}). Running in Safe Fallback Mode.")
else:
    print("INFO: Valid MONGO_URI not found. Running in Safe Fallback Mode.")


@app.route("/")
def index():
    if db_connected and products_col is not None:
        products = list(products_col.find({}, {"_id": 0}).sort("id", 1))
    else:
        products = INITIAL_PRODUCTS
    return render_template("index.html", products=products)


@app.route("/api/order", methods=["POST"])
def create_order():
    data = request.json
    if not data or not data.get("customer_name") or not data.get("phone") or not data.get("items"):
        return jsonify({"status": "error", "message": "Please fill all required fields."}), 400

    order_id = f"NC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    order_doc = {
        "order_id": order_id,
        "customer_name": data["customer_name"],
        "phone": data["phone"],
        "address": data.get("address", ""),
        "payment_method": data.get("payment_method", "Cash on Delivery"),
        "items": data["items"],
        "total_amount": data.get("total_amount", 0),
        "status": "Confirmed",
        "created_at": datetime.utcnow().isoformat()
    }

    if db_connected and orders_col is not None:
        orders_col.insert_one(order_doc)
    else:
        local_orders.append(order_doc)

    return jsonify({"status": "success", "order_id": order_id, "message": "Order placed successfully!"})


@app.route("/api/contact", methods=["POST"])
def save_contact():
    data = request.json
    if not data or not data.get("name") or not data.get("message"):
        return jsonify({"status": "error", "message": "Name and message are required."}), 400

    msg_doc = {
        "name": data["name"],
        "phone": data.get("phone", ""),
        "subject": data.get("subject", "General Inquiry"),
        "message": data["message"],
        "created_at": datetime.utcnow().isoformat()
    }

    if db_connected and messages_col is not None:
        messages_col.insert_one(msg_doc)
    else:
        local_messages.append(msg_doc)

    return jsonify({"status": "success", "message": "Thank you! Md. Rahat Howlader will contact you shortly."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)