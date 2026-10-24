import os
import sqlite3
import pandas as pd
import joblib
from flask import Flask, request, jsonify, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import init_db, get_db_connection
import requests as http_requests

# Auto-load .env file if present in workspace
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ[k.strip()] = v.strip().strip("'\"")
        except Exception as e:
            print(f"Error loading .env file: {e}")
load_env_file()

def setup_demo_images():
    import shutil
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    brain_dir = r"C:\Users\mulra\.gemini\antigravity\brain\ab139e98-8be5-4926-9dba-23b80fb4d424"
    files_to_copy = {
        'sample_leaf_blight_1787247278970.png': 'sample_leaf_blight.png',
        'sample_powdery_mildew_1787247292832.png': 'sample_powdery_mildew.png',
        'sample_healthy_leaf_1787247308470.png': 'sample_healthy_leaf.png'
    }
    
    for src_name, dst_name in files_to_copy.items():
        src_path = os.path.join(brain_dir, src_name)
        dst_path = os.path.join(static_dir, dst_name)
        if os.path.exists(src_path):
            try:
                shutil.copy(src_path, dst_path)
                print(f"Copied demo image {dst_name} to static folder.")
            except Exception as e:
                print(f"Error copying demo image: {e}")

setup_demo_images()

app = Flask(__name__)
app.secret_key = "agripredict_secret_key"

# --- EMAIL CONFIGURATION (OPTIONAL) ---
# To enable real emails, uncomment below and provide your credentials.
# from flask_mail import Mail, Message
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
# app.config['MAIL_PASSWORD'] = 'your-app-password'
# mail = Mail(app)
# ---------------------------------------

# --- Load ML Models ---
try:
    yield_model = joblib.load('models/yield_prediction_model.pkl')
    crop_model = joblib.load('models/crop_recommendation_model.pkl')
    MODELS_LOADED = True
    print("AI Models loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load AI models. {e}")
    MODELS_LOADED = False

def send_professional_email(to_email, subject, body_html):
    """Simulates sending a professional HTML email."""
    print(f"\n[EMAIL SENT TO: {to_email}]")
    print(f"Subject: {subject}")
    print("----- HTML BODY START -----")
    print(body_html)
    print("----- HTML BODY END -----\n")

VALID_RANGES = {

    'N': (0, 300),
    'P': (0, 150),
    'K': (0, 300),
    'pH': (3.5, 10.0),
    'avg_temp_c': (10, 45),
    'total_rainfall_mm': (0, 3000),
    'area': (0.1, 100)
}


# Initialize the database
if not os.path.exists('agripredict.db'):
    init_db()


# --- Page Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/marketplace')
def marketplace():
    return render_template('marketplace.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')


# --- API Routes ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    role = data.get('role')
    phone = data.get('phone', '')
    location = data.get('location', '')
    requirements = data.get('requirements', '')
    
    if not all([name, email, data.get('password'), role]):
        return jsonify({'error': 'Missing fields'}), 400
        
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (name, email, password, role, phone, location, requirements) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (name, email, password, role, phone, location, requirements))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Email already exists'}), 409
        
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    # Registration Email
    email_html = f"""
    <div style="font-family: Arial, sans-serif; border: 1px solid #2ecc71; padding: 20px; border-radius: 10px;">
        <h2 style="color: #2ecc71;">Welcome to AgriPredict, {name}!</h2>
        <p>Your professional agricultural account as a <strong>{role}</strong> has been successfully created.</p>
        <p>Explore our AI-driven marketplace and supply chain tools to grow your business.</p>
        <br>
        <p style="font-size: 0.8rem; color: #777;">&copy; 2026 AgriPredict Platform</p>
    </div>
    """
    send_professional_email(email, "Account Verified - AgriPredict", email_html)
    
    return jsonify({'message': 'User registered successfully', 'user': dict(user)}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return jsonify({'user': dict(user)}), 200
    return jsonify({'error': 'Invalid credentials'}), 401


# --- Marketplace & Deals ---

@app.route('/api/marketplace', methods=['GET'])
def get_listings():
    conn = get_db_connection()
    listings = conn.execute('''
        SELECT l.*, u.name as farmer_name, u.location as farmer_location, u.phone as farmer_phone
        FROM listings l 
        JOIN users u ON l.farmer_id = u.id
        WHERE status = 'Available'
        ORDER BY l.id DESC
    ''').fetchall()

    conn.close()
    return jsonify([dict(row) for row in listings]), 200

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        def get_val(keys, default=0):
            for k in keys:
                if k in data and data[k] is not None:
                    try:
                        return float(data[k])
                    except:
                        return default
            return default

        # 1. Server-side Validation
        vals = {
            'N': get_val(['n', 'N'], 50),
            'P': get_val(['p', 'P'], 30),
            'K': get_val(['k', 'K'], 30),
            'pH': get_val(['ph', 'pH'], 6.5),
            'avg_temp_c': get_val(['temp', 'avg_temp_c'], 25),
            'total_rainfall_mm': get_val(['rain', 'total_rainfall_mm'], 1000),
            'area': get_val(['area', 'land_area'], 1.0)
        }

        for field, (vmin, vmax) in VALID_RANGES.items():
            if vals[field] < vmin or vals[field] > vmax:
                field_label = field.replace('_', ' ').title()
                return jsonify({
                    'error': f"Invalid {field_label} value. Must be between {vmin} and {vmax}."
                }), 400

        input_data = pd.DataFrame([{
            'state': str(data.get('state', 'Global')).strip(),
            'crop': str(data.get('crop_for_yield', 'Rice')).strip(),
            'season': str(data.get('season_for_yield', 'Whole Year')).strip(),
            'area': vals['area'],
            'N': vals['N'],
            'P': vals['P'],
            'K': vals['K'],
            'pH': vals['pH'],
            'avg_temp_c': vals['avg_temp_c'],
            'total_rainfall_mm': vals['total_rainfall_mm']
        }])

        # 1. Predict Yield
        yld = 0
        if MODELS_LOADED and yield_model:
            yld = yield_model.predict(input_data)[0]
        else:
            yld = vals['area'] * 2.5 # Mock logic
        
        # 2. Recommend Top 3 Crops
        top_crops = []
        if MODELS_LOADED and crop_model:
            input_data_crop = input_data[['state', 'N', 'P', 'K', 'pH', 'avg_temp_c', 'total_rainfall_mm']]
            probs = crop_model.predict_proba(input_data_crop)[0]
            classes = crop_model.classes_
            
            # Combine, sort, and take top 3
            results = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)[:3]
            top_crops = [{"crop": str(c), "suitability": round(float(p) * 100, 1)} for c, p in results]
        else:
            top_crops = [
                {"crop": "Rice", "suitability": 85.5},
                {"crop": "Wheat", "suitability": 65.2},
                {"crop": "Maize", "suitability": 45.1}
            ]

        return jsonify({
            'yield': round(float(yld), 2),
            'recommendations': top_crops,
            'most_suitable': top_crops[0]['crop'] if top_crops else "Unknown"
        }), 200
    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({'error': 'An unexpected error occurred during analysis.'}), 500


@app.route('/api/marketplace', methods=['POST'])
def post_listing():
    data = request.json
    farmer_id = data.get('farmer_id')
    crop_name = data.get('crop_name')
    quantity_tons = data.get('quantity_tons')
    price_per_ton = data.get('price_per_ton')

    if not all([farmer_id, crop_name, quantity_tons, price_per_ton]):
        return jsonify({'error': 'Missing listing data'}), 400

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO listings (farmer_id, crop_name, quantity_tons, price_per_ton, status)
        VALUES (?, ?, ?, ?, 'Available')
    ''', (farmer_id, crop_name, quantity_tons, price_per_ton))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Listing posted successfully!'}), 201

@app.route('/api/my_listings', methods=['GET'])
def get_my_listings():
    farmer_id = request.args.get('farmer_id')
    if not farmer_id:
        return jsonify({'error': 'Missing farmer_id'}), 400
    
    conn = get_db_connection()
    listings = conn.execute('SELECT * FROM listings WHERE farmer_id = ? ORDER BY id DESC', (farmer_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in listings]), 200

@app.route('/api/user/orders', methods=['GET'])
def get_user_orders():
    user_id = request.args.get('user_id')
    role = request.args.get('role')
    if not user_id or not role:
        return jsonify({'error': 'Missing user_id or role'}), 400
    
    conn = get_db_connection()
    if role == 'Farmer':
        txns = conn.execute('''
            SELECT t.*, u_v.name as partner_name, l.crop_name
            FROM transactions t
            JOIN users u_v ON t.vendor_id = u_v.id
            JOIN listings l ON t.listing_id = l.id
            WHERE t.farmer_id = ?
            ORDER BY t.timestamp DESC
        ''', (int(user_id),)).fetchall()
    else: # Vendor
        txns = conn.execute('''
            SELECT t.*, u_f.name as partner_name, l.crop_name
            FROM transactions t
            JOIN users u_f ON t.farmer_id = u_f.id
            JOIN listings l ON t.listing_id = l.id
            WHERE t.vendor_id = ?
            ORDER BY t.timestamp DESC
        ''', (int(user_id),)).fetchall()
    
    conn.close()
    return jsonify([dict(row) for row in txns]), 200

@app.route('/api/express_interest', methods=['POST'])
def express_interest():
    data = request.json
    listing_id = data.get('listing_id')
    vendor_id = data.get('vendor_id')

    conn = get_db_connection()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    farmer = conn.execute('SELECT * FROM users WHERE id = ?', (listing['farmer_id'],)).fetchone()
    vendor = conn.execute('SELECT * FROM users WHERE id = ?', (vendor_id,)).fetchone()
    admin = conn.execute('SELECT * FROM users WHERE role = "Admin"').fetchone()

    quantity_set = float(data.get('quantity_set', listing['quantity_tons']))
    total_price = quantity_set * listing['price_per_ton']

    # Create transaction record with Paid_OrderPlaced status
    conn.execute('''
        INSERT INTO transactions (listing_id, vendor_id, farmer_id, total_price, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (listing_id, vendor_id, listing['farmer_id'], total_price, 'Paid_OrderPlaced'))
    conn.commit()
    conn.close()

    # Notify parties
    email_html = f"""
    <div style="font-family: Arial, sans-serif; border: 1px solid #3498db; padding: 20px; border-radius: 10px;">
        <h2 style="color: #3498db;">📦 New Order Placed: SCM Initiated</h2>
        <p>A new order for your crop listing has been placed. <strong>AgriPredict SCM</strong> is now managing the delivery.</p>
        <p><strong>Deal Value:</strong> ₹{listing['quantity_tons'] * listing['price_per_ton']}</p>
        <p>The Admin will contact you shortly to coordinate logistics.</p>
    </div>
    """
    send_professional_email(farmer['email'], "New Order Received - SCM Initiated", email_html)
    
    if admin:
        send_professional_email(admin['email'], "SCM Alert: New Order", f"<p>Order placed by Vendor {vendor['name']} for Farmer {farmer['name']}'s {listing['crop_name']}. Please oversee SCM delivery.</p>")

    return jsonify({'message': 'Order Placed! System Admin will contact you for SCM and delivery.'}), 201


@app.route('/api/admin/support_tickets', methods=['GET'])
def get_support_tickets():
    conn = get_db_connection()
    tickets = conn.execute('''
        SELECT t.*, u.name as user_name, u.role as user_role, u.email as user_email
        FROM support_tickets t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.timestamp DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in tickets]), 200

@app.route('/api/admin/transactions', methods=['GET'])
def get_admin_transactions():
    conn = get_db_connection()
    txns = conn.execute('''
        SELECT t.*, u_f.name as farmer_name, u_f.phone as farmer_phone, u_f.email as farmer_email,
               u_v.name as vendor_name, u_v.phone as vendor_phone, u_v.email as vendor_email, l.crop_name
        FROM transactions t
        JOIN users u_f ON t.farmer_id = u_f.id
        JOIN users u_v ON t.vendor_id = u_v.id
        JOIN listings l ON t.listing_id = l.id
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in txns]), 200

@app.route('/api/admin/share_contacts', methods=['POST'])
def share_contacts():
    # Now treated as "Approve SCM"
    txn_id = request.json.get('transaction_id')
    conn = get_db_connection()
    txn = conn.execute('''
        SELECT t.*, u_f.name as f_name, u_f.email as f_email, u_f.phone as f_phone,
               u_v.name as v_name, u_v.email as v_email, u_v.phone as v_phone
        FROM transactions t
        JOIN users u_f ON t.farmer_id = u_f.id
        JOIN users u_v ON t.vendor_id = u_v.id
        WHERE t.id = ?
    ''', (txn_id,)).fetchone()

    # Send contacts
    send_professional_email(txn['f_email'], "Delivery Initiated", f"AgriPredict SCM has initiated delivery. Contact {txn['v_name']} at {txn['v_phone']}.")
    send_professional_email(txn['v_email'], "Delivery Initiated", f"AgriPredict SCM has initiated delivery. Contact {txn['f_name']} at {txn['f_phone']}.")

    conn.execute('UPDATE transactions SET status = "SCM_Managed" WHERE id = ?', (txn_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'SCM Managed - Contact info shared for logistics.'}), 200

@app.route('/api/admin/finalize_deal', methods=['POST'])
def finalize_deal():
    txn_id = request.json.get('transaction_id')
    conn = get_db_connection()
    txn = conn.execute('SELECT * FROM transactions WHERE id = ?', (txn_id,)).fetchone()
    
    commission = txn['total_price'] * 0.30  # 30% cut including transport
    conn.execute('UPDATE transactions SET status = "Finalized", commission = ? WHERE id = ?', (commission, txn_id))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Deal Finalized! 30% cut (including SCM cost) recorded: ₹{commission:.2f}'}), 200

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    conn = get_db_connection()
    total_rev = conn.execute('SELECT SUM(commission) FROM transactions WHERE status = "Finalized"').fetchone()[0] or 0
    farmer_count = conn.execute('SELECT COUNT(*) FROM users WHERE role = "Farmer"').fetchone()[0]
    vendor_count = conn.execute('SELECT COUNT(*) FROM users WHERE role = "Vendor"').fetchone()[0]
    
    # Marketing dummy data
    marketing_pie = {'Facebook': 45, 'Instagram': 35, 'Direct Ads': 20}
    
    # Feedback Problem identification chart
    feedback_stats = {
        'Technical': conn.execute('SELECT COUNT(*) FROM support_tickets WHERE category="Technical"').fetchone()[0],
        'Billing': conn.execute('SELECT COUNT(*) FROM support_tickets WHERE category="Billing"').fetchone()[0],
        'SCM / Delivery': conn.execute('SELECT COUNT(*) FROM support_tickets WHERE category="Logistics"').fetchone()[0],
        'General': conn.execute('SELECT COUNT(*) FROM support_tickets WHERE category="General"').fetchone()[0]
    }

    # User Directory (Limited to 50 for display)
    users = conn.execute('SELECT name, role, email, phone, location, requirements FROM users LIMIT 50').fetchall()
    
    conn.close()
    return jsonify({
        'revenue': total_rev,
        'farmers': farmer_count,
        'vendors': vendor_count,
        'marketing': marketing_pie,
        'feedback': feedback_stats,
        'users': [dict(row) for row in users]
    }), 200


# --- Prediction Endpoints ---

@app.route('/api/recommend_crop', methods=['POST'])
def recommend_crop():
    data = request.json
    try:
        if not MODELS_LOADED:
            return jsonify({'recommended_crop': 'Maize (Mock Advisor)', 'mock': True})
        
        # Consistent helper for case-insensitivity
        def get_val(keys, default=0):
            for k in keys:
                if k in data and data[k] is not None:
                    return data[k]
            return default

        input_data = {
            'state': str(data.get('state', 'Global')).strip(),
            'N': float(get_val(['n', 'N'], 50)),
            'P': float(get_val(['p', 'P'], 30)),
            'K': float(get_val(['k', 'K'], 30)),
            'pH': float(get_val(['ph', 'pH'], 6.5)),
            'avg_temp_c': float(get_val(['temp', 'avg_temp_c'], 25)),
            'total_rainfall_mm': float(get_val(['rain', 'total_rainfall_mm'], 1000))
        }
        
        df = pd.DataFrame([input_data])
        crop = crop_model.predict(df)[0]
        return jsonify({'recommended_crop': crop})
    except Exception as e:
        print(f"Recommendation Error: {e}")
        return jsonify({'error': 'Recommendation error'}), 500

@app.route('/api/predict_yield', methods=['POST'])
def predict_yield():
    data = request.json
    try:
        if not MODELS_LOADED:
            return jsonify({'yield_tons': round(float(data.get('area', 10)) * 2.5, 2), 'mock': True})
            
        def get_val(keys, default=0):
            for k in keys:
                if k in data and data[k] is not None:
                    return data[k]
            return default

        input_data = {
            'state': str(data.get('state', 'Global')).strip(),
            'crop': str(get_val(['crop_for_yield', 'crop'], 'Rice')).strip(),
            'season': str(get_val(['season_for_yield', 'season'], 'Whole Year')).strip(),
            'area': float(get_val(['area', 'land_area'], 1.0)),
            'N': float(get_val(['n', 'N'], 50)),
            'P': float(get_val(['p', 'P'], 30)),
            'K': float(get_val(['k', 'K'], 30)),
            'pH': float(get_val(['ph', 'pH'], 6.5)),
            'avg_temp_c': float(get_val(['temp', 'avg_temp_c'], 25)),
            'total_rainfall_mm': float(get_val(['rain', 'total_rainfall_mm'], 1000))
        }
        
        df = pd.DataFrame([input_data])
        prediction = yield_model.predict(df)[0]
        return jsonify({'yield_tons': round(prediction, 2)})
    except Exception as e:
        print(f"Yield Prediction Error: {e}")
        return jsonify({'error': 'Prediction error'}), 500

@app.route('/api/support', methods=['POST'])
def post_support():
    data = request.json
    conn = get_db_connection()
    conn.execute('INSERT INTO support_tickets (user_id, message, category) VALUES (?, ?, ?)',
                 (data.get('user_id'), data.get('message'), data.get('category', 'General')))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Support request submitted.'}), 201

# =====================================================
# FEATURE 1: OpenWeatherMap Live Weather API
# =====================================================

OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Realistic weather defaults per state for offline / fallback mode
STATE_WEATHER_DEFAULTS = {
    'Maharashtra': {'temperature_c': 30.5, 'humidity_pct': 72.0, 'rainfall_mm': 15.0, 'desc': 'Partly Cloudy'},
    'Rajasthan': {'temperature_c': 35.8, 'humidity_pct': 38.0, 'rainfall_mm': 2.0, 'desc': 'Hot & Dry'},
    'Punjab': {'temperature_c': 27.2, 'humidity_pct': 58.0, 'rainfall_mm': 5.0, 'desc': 'Clear Sky'},
    'Haryana': {'temperature_c': 28.5, 'humidity_pct': 55.0, 'rainfall_mm': 4.0, 'desc': 'Clear Sky'},
    'Uttar Pradesh': {'temperature_c': 29.0, 'humidity_pct': 64.0, 'rainfall_mm': 8.0, 'desc': 'Hazy Sunshine'},
    'Madhya Pradesh': {'temperature_c': 31.0, 'humidity_pct': 50.0, 'rainfall_mm': 6.0, 'desc': 'Warm & Clear'},
    'Gujarat': {'temperature_c': 33.2, 'humidity_pct': 60.0, 'rainfall_mm': 3.5, 'desc': 'Sunny'},
    'Karnataka': {'temperature_c': 26.8, 'humidity_pct': 75.0, 'rainfall_mm': 18.0, 'desc': 'Moderate Rain'},
    'Tamil Nadu': {'temperature_c': 32.0, 'humidity_pct': 70.0, 'rainfall_mm': 10.0, 'desc': 'Tropical Warmth'},
    'Kerala': {'temperature_c': 28.0, 'humidity_pct': 85.0, 'rainfall_mm': 45.0, 'desc': 'Heavy Showers'},
    'Andhra Pradesh': {'temperature_c': 31.5, 'humidity_pct': 68.0, 'rainfall_mm': 11.0, 'desc': 'Humid'},
    'Telangana': {'temperature_c': 32.5, 'humidity_pct': 55.0, 'rainfall_mm': 7.0, 'desc': 'Sunny'},
    'West Bengal': {'temperature_c': 29.8, 'humidity_pct': 80.0, 'rainfall_mm': 22.0, 'desc': 'Humid & Overcast'},
    'Bihar': {'temperature_c': 28.4, 'humidity_pct': 70.0, 'rainfall_mm': 14.0, 'desc': 'Scattered Clouds'},
    'Assam': {'temperature_c': 26.0, 'humidity_pct': 88.0, 'rainfall_mm': 35.0, 'desc': 'Light Rain'},
}

@app.route('/api/get-weather', methods=['GET'])
def get_weather():
    """Fetch live weather data from OpenWeatherMap API.
    Accepts: ?lat=XX&lon=YY  OR  ?city=CityName
    Returns: temperature (°C), humidity (%), rainfall (mm).
    """
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    city = request.args.get('city', '')

    api_key = os.environ.get('OPENWEATHER_API_KEY', '').strip()

    # Get state-specific default fallback data
    st_data = STATE_WEATHER_DEFAULTS.get(city)
    if st_data:
        fallback = {
            'temperature_c': st_data['temperature_c'],
            'humidity_pct': st_data['humidity_pct'],
            'rainfall_mm': st_data['rainfall_mm'],
            'city': city,
            'description': st_data['desc'],
            'source': 'fallback'
        }
    else:
        # Generate unique temperature based on city hash if state not in list
        city_hash = sum(ord(c) for c in city) if city else 28
        temp_val = round(25.0 + (city_hash % 12), 1)
        fallback = {
            'temperature_c': temp_val,
            'humidity_pct': 65.0,
            'rainfall_mm': 5.0,
            'city': city or 'Unknown',
            'description': 'Estimated seasonal weather',
            'source': 'fallback'
        }

    if not api_key or 'your_' in api_key.lower():
        fallback['description'] = 'Offline mode (OPENWEATHER_API_KEY not set)'
        return jsonify(fallback), 200

    try:
        params: dict = {'appid': api_key, 'units': 'metric'}
        if lat and lon:
            params['lat'] = lat
            params['lon'] = lon
        elif city:
            params['q'] = city
        else:
            return jsonify({'error': 'Provide lat & lon, or city parameter.'}), 400

        resp = http_requests.get(OPENWEATHER_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Extract rainfall (may not always be present)
        rainfall = 0.0
        if 'rain' in data:
            rainfall = data['rain'].get('1h', data['rain'].get('3h', 0.0))

        return jsonify({
            'temperature_c': round(data['main']['temp'], 1),
            'humidity_pct': data['main']['humidity'],
            'rainfall_mm': round(rainfall, 2),
            'city': data.get('name', 'Unknown'),
            'description': data['weather'][0]['description'] if data.get('weather') else '',
            'source': 'openweathermap_live'
        }), 200

    except Exception as e:
        print(f"Weather API Error: {e}")
        return jsonify(fallback), 200


# =====================================================
# FEATURE 2: CNN Crop Disease Classifier
# =====================================================

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Lazy-load classifier to avoid import errors if torch not installed
_disease_classifier = None
def get_disease_classifier():
    global _disease_classifier
    if _disease_classifier is None:
        try:
            from ml_pipeline import CropDiseaseClassifier
            _disease_classifier = CropDiseaseClassifier()
        except ImportError:
            _disease_classifier = None
    return _disease_classifier

@app.route('/api/predict-disease', methods=['POST'])
def predict_disease():
    """CNN-based crop disease prediction from uploaded leaf image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded. Use field name: image'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png'}), 400

    # Sanitize and save
    safe_name = secure_filename(file.filename)
    timestamp_prefix = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S_')
    safe_name = timestamp_prefix + safe_name
    filepath = os.path.join(UPLOAD_FOLDER, safe_name)
    file.save(filepath)

    # Run CNN prediction
    classifier = get_disease_classifier()
    if classifier is None:
        result = {
            'disease': 'Service Unavailable',
            'confidence': 0.0,
            'treatment': 'Install torch and torchvision to enable disease classification.',
            'severity': 'Unknown',
            'mock': True
        }
    else:
        result = classifier.predict(filepath)

    result['image_filename'] = safe_name

    # Log to database
    try:
        user_id = request.form.get('user_id')
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO disease_logs (user_id, image_filename, predicted_disease, confidence, treatment_advice) VALUES (?, ?, ?, ?, ?)',
            (user_id, safe_name, result['disease'], result['confidence'], result['treatment'])
        )
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"Disease log DB error: {db_err}")

    return jsonify(result), 200


# =====================================================
# FEATURE 3: Gemini LLM Platform Assistant Chatbot
# =====================================================

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

AGRIPREDICT_SYSTEM_PROMPT = """You are AgriPredict Assistant — the official AI helper for the AgriPredict B2B Agri-Tech Platform (India).

HOW TO RESPOND BASED ON USER INTENT:

1. USER REGISTRATION & AUTHENTICATION INTENT (e.g. "how register user", "how to sign up", "create account", "login", "register"):
   Explain clearly step-by-step:
   - Click 'Sign In' / 'Register' button on the top navigation bar.
   - Choose your role: 'Farmer' or 'Vendor'.
   - Enter your Name, Email, Password, Phone Number, and Location.
   - Click 'Create Account'. You will receive a verification email and full access to AI predictors, CNN disease classifier, and marketplace.
   - DO NOT ask for State or Land Area when the user asks how to register or create an account!

2. CNN CROP DISEASE PREDICTION INTENT (e.g. "disease", "cnn", "leaf scan", "crop disease", "recognize disease", "how cnn works"):
   Explain clearly:
   - AgriPredict includes an advanced CNN (Convolutional Neural Network) Crop Leaf Classifier using MobileNetV2 architecture!
   - How to use & recognize it working: Go to Dashboard -> Scroll to 'CNN Crop Disease Classifier' -> Upload/drag a leaf photo (JPG/PNG) -> Click 'Scan Crop Leaf with CNN AI'.
   - The CNN model analyzes leaf patterns and displays identified disease, confidence score (%), severity, and recommended treatment advice!

3. CROP ADVICE & YIELD PREDICTION INTENT (When asking for crops or state recommendations):
   - When a user asks for crop recommendation by providing their State (e.g., "My state is Maharashtra"):
     a) Recommend the primary crop and alternative crop for that state along with ideal soil N-P-K defaults and market price per ton.
     b) IF THE USER DID NOT SPECIFY THEIR LAND AREA (Hectares/Acres), ASK THEM: "How many Hectares or Acres of land do you have?" so you can calculate total yield and revenue.
     c) IF THE USER PROVIDED BOTH STATE AND LAND AREA (e.g. "Maharashtra 5 hectares"), calculate total yield (tons), market price (₹/ton), revenue, and output structured JSON:
     ###FORM_DATA###{"state":"StateName","area":AreaInHa,"n":N_val,"p":P_val,"k":K_val,"ph":pH_val,"temp":Temp_val,"rain":Rain_val,"crop":"CropName","season":"SeasonName"}###END_FORM###

4. MARKETPLACE & SUPPLY CHAIN (SCM) INTENT:
   - Explain listing, Razorpay purchases, and 3-stage SCM delivery (Paid_OrderPlaced -> SCM_Managed -> Finalized with 30% commission).

Always answer in the language requested (English or Hindi). Be concise, helpful, and polite."""

# Market price lookup dictionary (₹ per ton)
CROP_MARKET_PRICES = {
    'Rice': 22000, 'Wheat': 24000, 'Maize': 19500, 'Cotton': 62000,
    'Sugarcane': 3200, 'Chickpea': 52000, 'Kidneybeans': 65000, 'Pigeonpeas': 60000,
    'Mothbeans': 55000, 'Mungbean': 70000, 'Blackgram': 68000, 'Lentil': 58000,
    'Pomegranate': 85000, 'Banana': 18000, 'Mango': 45000, 'Grapes': 60000,
    'Watermelon': 12000, 'Muskmelon': 15000, 'Apple': 90000, 'Orange': 35000,
    'Papaya': 20000, 'Coconut': 35000, 'Jute': 42000, 'Coffee': 140000
}

# State crop recommendations & soil defaults
STATE_RECOMMENDED_CROPS = {
    'Maharashtra': {'crop': 'Rice', 'alt': 'Cotton', 'season': 'Kharif', 'n': 90, 'p': 42, 'k': 43, 'ph': 6.5, 'temp': 30.5, 'rain': 1200, 'yield_per_ha': 4.8},
    'Rajasthan': {'crop': 'Wheat', 'alt': 'Chickpea', 'season': 'Rabi', 'n': 70, 'p': 35, 'k': 30, 'ph': 7.2, 'temp': 32.0, 'rain': 450, 'yield_per_ha': 3.5},
    'Punjab': {'crop': 'Wheat', 'alt': 'Rice', 'season': 'Rabi', 'n': 100, 'p': 50, 'k': 40, 'ph': 6.8, 'temp': 27.0, 'rain': 650, 'yield_per_ha': 5.2},
    'Haryana': {'crop': 'Wheat', 'alt': 'Maize', 'season': 'Rabi', 'n': 95, 'p': 45, 'k': 38, 'ph': 7.0, 'temp': 28.0, 'rain': 550, 'yield_per_ha': 4.9},
    'Uttar Pradesh': {'crop': 'Sugarcane', 'alt': 'Wheat', 'season': 'Kharif', 'n': 110, 'p': 48, 'k': 45, 'ph': 6.6, 'temp': 29.0, 'rain': 950, 'yield_per_ha': 65.0},
    'Madhya Pradesh': {'crop': 'Chickpea', 'alt': 'Maize', 'season': 'Kharif', 'n': 80, 'p': 40, 'k': 35, 'ph': 6.8, 'temp': 30.0, 'rain': 800, 'yield_per_ha': 3.2},
    'Gujarat': {'crop': 'Cotton', 'alt': 'Maize', 'season': 'Kharif', 'n': 85, 'p': 40, 'k': 45, 'ph': 7.1, 'temp': 33.0, 'rain': 700, 'yield_per_ha': 2.8},
    'Karnataka': {'crop': 'Coffee', 'alt': 'Maize', 'season': 'Kharif', 'n': 85, 'p': 45, 'k': 50, 'ph': 6.2, 'temp': 26.5, 'rain': 1400, 'yield_per_ha': 1.8},
    'Tamil Nadu': {'crop': 'Rice', 'alt': 'Coconut', 'season': 'Whole Year', 'n': 90, 'p': 45, 'k': 50, 'ph': 6.4, 'temp': 32.0, 'rain': 1100, 'yield_per_ha': 4.6},
    'Kerala': {'crop': 'Coconut', 'alt': 'Banana', 'season': 'Whole Year', 'n': 75, 'p': 40, 'k': 60, 'ph': 5.8, 'temp': 28.0, 'rain': 2200, 'yield_per_ha': 12.0},
    'West Bengal': {'crop': 'Jute', 'alt': 'Rice', 'season': 'Kharif', 'n': 90, 'p': 45, 'k': 45, 'ph': 6.3, 'temp': 29.5, 'rain': 1600, 'yield_per_ha': 3.6},
    'Bihar': {'crop': 'Maize', 'alt': 'Rice', 'season': 'Kharif', 'n': 85, 'p': 40, 'k': 38, 'ph': 6.7, 'temp': 28.5, 'rain': 1150, 'yield_per_ha': 4.2},
    'Andhra Pradesh': {'crop': 'Rice', 'alt': 'Maize', 'season': 'Kharif', 'n': 92, 'p': 46, 'k': 42, 'ph': 6.6, 'temp': 31.0, 'rain': 1000, 'yield_per_ha': 4.7},
    'Telangana': {'crop': 'Cotton', 'alt': 'Rice', 'season': 'Kharif', 'n': 88, 'p': 42, 'k': 40, 'ph': 6.7, 'temp': 32.0, 'rain': 900, 'yield_per_ha': 2.7}
}

# Hindi to English State Mapping for Voice Recognition
HINDI_STATE_MAP = {
    'महाराष्ट्र': 'Maharashtra', 'महारास्ट्र': 'Maharashtra',
    'राजस्थान': 'Rajasthan', 'पंजाब': 'Punjab', 'हरियाणा': 'Haryana',
    'उत्तर प्रदेश': 'Uttar Pradesh', 'यूपी': 'Uttar Pradesh', 'उप्र': 'Uttar Pradesh',
    'मध्य प्रदेश': 'Madhya Pradesh', 'एमपी': 'Madhya Pradesh', 'मप्र': 'Madhya Pradesh',
    'गुजरात': 'Gujarat', 'कर्नाटक': 'Karnataka', 'तमिलनाडु': 'Tamil Nadu', 'तमिल नाडू': 'Tamil Nadu',
    'केरल': 'Kerala', 'पश्चिम बंगाल': 'West Bengal', 'बंगाल': 'West Bengal',
    'बिहार': 'Bihar', 'आंध्र प्रदेश': 'Andhra Pradesh', 'आंध्र': 'Andhra Pradesh',
    'तेलंगाना': 'Telangana', 'असम': 'Assam', 'ओडिशा': 'Odisha', 'उड़ीसा': 'Odisha',
    'छत्तीसगढ़': 'Chhattisgarh', 'झारखंड': 'Jharkhand', 'उत्तराखंड': 'Uttarakhand',
    'हिमाचल': 'Himachal Pradesh', 'गोवा': 'Goa'
}

HINDI_NUMBERS = {
    'एक': 1, 'दो': 2, 'तीन': 3, 'चार': 4, 'पाँच': 5, 'पांच': 5,
    'छह': 6, 'सात': 7, 'आठ': 8, 'नौ': 9, 'दस': 10,
    'पंद्रह': 15, 'बीस': 20, 'पच्चीस': 25, 'तीस': 30, 'पचास': 50, 'सौ': 100
}

@app.route('/api/chat', methods=['POST'])
def chat():
    """Gemini LLM chatbot with voice support, form-filling, and multi-language."""
    import re
    data = request.json or {}
    user_message = data.get('message', '').strip()
    user_id = data.get('user_id')
    user_lang = data.get('lang', 'en-IN')

    if not user_message:
        return jsonify({'error': 'Message is required.'}), 400

    gemini_key = os.environ.get('GEMINI_API_KEY', '').strip()
    bot_response = ''
    form_data = None

    msg_lower = user_message.lower()
    is_hindi = ('hi' in user_lang) or bool(re.search(r'[\u0900-\u097F]', user_message))

    # Always attempt online Gemini API if valid key is set
    if gemini_key and not ('your_' in gemini_key.lower()):
        try:
            import google.generativeai as genai
            import json as json_lib
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                system_instruction=AGRIPREDICT_SYSTEM_PROMPT
            )
            response = model.generate_content(user_message)
            bot_response = response.text

            # Extract form data if present
            if '###FORM_DATA###' in bot_response and '###END_FORM###' in bot_response:
                try:
                    json_str = bot_response.split('###FORM_DATA###')[1].split('###END_FORM###')[0]
                    form_data = json_lib.loads(json_str)
                    bot_response = bot_response.split('###FORM_DATA###')[0].strip()
                except (json_lib.JSONDecodeError, IndexError):
                    pass

        except Exception as e:
            print(f"Gemini API Error: {e}")
            bot_response = ""

    # If no response yet (no key or Gemini API error), use Built-in AgriPredict Intent Engine
    if not bot_response:
        # 1. INTENT: Registration / Signup / User Account
        if any(w in msg_lower for w in ['register', 'registration', 'signup', 'sign up', 'create account', 'regis', 'पंजीकरण', 'रजिस्टर', 'खाता']):
            if is_hindi:
                bot_response = (
                    "📝 **एग्रीप्रेडिक्ट पर रजिस्टर (पंजीकरण) कैसे करें**:\n\n"
                    "1️⃣ सबसे ऊपर दाहिने कोने में **Sign In / Register** बटन पर क्लिक करें।\n"
                    "2️⃣ अपनी भूमिका चुनें: **किसान (Farmer)** या **बी2बी व्यापारी (Vendor)**।\n"
                    "3️⃣ अपना नाम, ईमेल, पासवर्ड, फोन नंबर और स्थान दर्ज करें।\n"
                    "4️⃣ **Create Account** बटन दबाएं।\n\n"
                    "🎉 इसके बाद आपको तुरंत अकाउंट कन्फर्मेशन ईमेल मिलेगा और आप एआई प्रेडिक्शन तथा मार्केटप्लेस का उपयोग कर सकेंगे!"
                )
            else:
                bot_response = (
                    "📝 **How to Register a User on AgriPredict**:\n\n"
                    "1️⃣ Click on **Sign In / Register** at the top right of the navigation bar.\n"
                    "2️⃣ Choose your account role (**Farmer** or **B2B Vendor**).\n"
                    "3️⃣ Enter your Name, Email, Password, Phone Number, and Location.\n"
                    "4️⃣ Click the **Create Account** button.\n\n"
                    "🎉 You will receive an instant welcome verification email and gain immediate access to AI predictors, CNN disease detection, and marketplace trading!"
                )

        # 2. INTENT: Login / Authentication
        elif any(w in msg_lower for w in ['login', 'log in', 'sign in', 'signin', 'लॉगिन', 'साइन इन']):
            if is_hindi:
                bot_response = "🔑 **लॉगिन करने का तरीका**: ऊपर **Sign In** पर क्लिक करें, अपना पंजीकृत ईमेल व पासवर्ड दर्ज करें और Sign In बटन दबाएं।"
            else:
                bot_response = "🔑 **How to Log In**: Click **Sign In** at the top right of the navbar, enter your registered Email and Password, and click **Sign In**."

        # 3. INTENT: CNN Crop Disease Prediction
        elif any(w in msg_lower for w in ['disease', 'cnn', 'leaf', 'scan', 'pathology', 'illness', 'spot', 'blight', 'रोग', 'बीमारी', 'पत्ती']):
            if is_hindi:
                bot_response = (
                    "🌿 **CNN फसल रोग पहचान (Crop Disease Classifier)**:\n\n"
                    "एग्रीप्रेडिक्ट में पत्तियों की फोटो से रोग पहचानने के लिए **Deep Learning CNN (MobileNetV2)** मॉडल इंटीग्रेटेड है!\n\n"
                    "**इस फीचर को जांचने का तरीका**:\n"
                    "1️⃣ **Dashboard** पेज खोलें।\n"
                    "2️⃣ **CNN Crop Disease Classifier** कार्ड पर जाएं।\n"
                    "3️⃣ किसी पौधे की पत्ती की फोटो (JPG/PNG) अपलोड करें।\n"
                    "4️⃣ **Scan Leaf with CNN AI** बटन दबाएं।\n"
                    "5️⃣ CNN मॉडल तुरंत रोग का नाम, सटीक % कॉन्फिडेंस, गंभीरता (Severity) और इलाज का सुझाव (Treatment Advice) दिखाएगा!"
                )
            else:
                bot_response = (
                    "🌿 **CNN Crop Disease Classifier Feature**:\n\n"
                    "AgriPredict uses a deep learning **Convolutional Neural Network (CNN)** (MobileNetV2) to classify crop leaf diseases!\n\n"
                    "**How to test & recognize it working**:\n"
                    "1️⃣ Navigate to the **Dashboard** page.\n"
                    "2️⃣ Find the **CNN Crop Disease Classifier** section.\n"
                    "3️⃣ Upload or drop a photo of a crop leaf (JPG/PNG).\n"
                    "4️⃣ Click **Scan Leaf with CNN AI**.\n"
                    "5️⃣ The CNN model will display the exact disease diagnosis, confidence score (%), severity level, and specific treatment advice!"
                )

        # 4. INTENT: Marketplace / Order / Buying / Selling
        elif any(w in msg_lower for w in ['marketplace', 'buy', 'sell', 'order', 'listing', 'खरीद', 'बेच']):
            if is_hindi:
                bot_response = "🛒 **मार्केटप्लेस निर्देश**: किसान डैशबोर्ड से फसल लिस्ट कर सकते हैं और व्यापारी सीधे Buy Now से खरीदारी कर सकते हैं।"
            else:
                bot_response = "🛒 **Marketplace Instructions**: Farmers can post crop listings with quantity and price per ton. Vendors can browse marketplace listings and click **Buy Now** to initiate purchase via AgriPredict SCM."

        # 5. INTENT: Specific State / Land / Crop Advice
        else:
            # Extract state, land area, NPK, crop
            extracted = {}
            target_state = None
            for st_eng in STATE_RECOMMENDED_CROPS.keys():
                if st_eng.lower() in msg_lower:
                    target_state = st_eng
                    extracted['state'] = st_eng
                    break

            if not target_state:
                for st_hi, st_eng in HINDI_STATE_MAP.items():
                    if st_hi in user_message:
                        target_state = st_eng
                        extracted['state'] = st_eng
                        break

            # Search explicitly for land area in user message
            area_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:hectare|hectares|ha|एकर|एकड़|हेक्टेयर|acre|acres)', user_message, re.I)
            has_explicit_area = False
            land_area = None

            if area_m:
                land_area = float(area_m.group(1))
                has_explicit_area = True
            else:
                for num_word, val in HINDI_NUMBERS.items():
                    if num_word in user_message and any(unit in msg_lower for unit in ['hectare', 'ha', 'acre', 'हेक्टेयर', 'एकड़']):
                        land_area = float(val)
                        has_explicit_area = True
                        break

            # Check crop specified
            target_crop = None
            for c in CROP_MARKET_PRICES.keys():
                if c.lower() in msg_lower:
                    target_crop = c
                    extracted['crop'] = c
                    break

            st_info = STATE_RECOMMENDED_CROPS.get(target_state, STATE_RECOMMENDED_CROPS['Maharashtra']) if target_state else STATE_RECOMMENDED_CROPS['Maharashtra']
            if not target_crop:
                target_crop = st_info['crop']
                extracted['crop'] = target_crop

            if target_state:
                extracted['state'] = target_state
                extracted['n'] = st_info['n']
                extracted['p'] = st_info['p']
                extracted['k'] = st_info['k']
                extracted['ph'] = st_info['ph']
                extracted['temp'] = st_info['temp']
                extracted['rain'] = st_info['rain']
                extracted['season'] = st_info['season']

            price_per_ton = CROP_MARKET_PRICES.get(target_crop, 22000)

            # CASE A: State specified, but NO explicit land area given yet
            if target_state and not has_explicit_area:
                if is_hindi:
                    bot_response = (
                        f"🌾 **{target_state} के लिए अनुशंसित फसल व मृदा सुझाव**:\n\n"
                        f"• **अनुशंसित फसल**: **{target_crop}** ({st_info['season']} सीजन, विकल्प: {st_info['alt']})\n"
                        f"• **मानक मृदा पोषण (N-P-K)**: N: {st_info['n']} | P: {st_info['p']} | K: {st_info['k']} (pH: {st_info['ph']})\n"
                        f"• **अनुमानित बाजार मूल्य**: ₹{price_per_ton:,} / टन\n\n"
                        f"❓ **कुल उपज (टन) और आय की गणना के लिए**: कृपया अपनी जमीन का आकार बताएं (जैसे **'5 हेक्टेयर'** या **'3 एकड़'**)!"
                    )
                else:
                    bot_response = (
                        f"🌾 **Crop & Soil Recommendation for {target_state}**:\n\n"
                        f"• **Recommended Crop**: **{target_crop}** ({st_info['season']} season, Alternative: {st_info['alt']})\n"
                        f"• **Recommended Soil N-P-K Values**: N: {st_info['n']} | P: {st_info['p']} | K: {st_info['k']} (pH: {st_info['ph']})\n"
                        f"• **Market Selling Price**: ₹{price_per_ton:,} / Ton\n\n"
                        f"❓ **To calculate your total yield (tons) & revenue**: How many Hectares or Acres of land do you have? (e.g. type **'5 hectares'** or **'10 acres'**)."
                    )

            # CASE B: Explicit land area provided with state (or alone)
            elif has_explicit_area and land_area:
                extracted['area'] = land_area
                yield_per_ha = st_info.get('yield_per_ha', 4.5)
                total_yield_tons = round(land_area * yield_per_ha, 1)
                total_revenue = int(total_yield_tons * price_per_ton)
                form_data = extracted

                st_display = target_state or "your region"
                if is_hindi:
                    bot_response = (
                        f"🌾 **{st_display} ({land_area} हेक्टेयर) के लिए संपूर्ण उपज व आय योजना**:\n\n"
                        f"1️⃣ **अनुशंसित फसल**: {target_crop} (विकल्प: {st_info['alt']})\n"
                        f"2️⃣ **अनुमानित कुल उपज**: ~{total_yield_tons} टन\n"
                        f"3️⃣ **सुझाया गया बाजार मूल्य**: ₹{price_per_ton:,} / टन\n"
                        f"4️⃣ **अनुमानित सकल आय**: ₹{total_revenue:,}\n"
                        f"5️⃣ **डैशबोर्ड फॉर्म**: फॉर्म ऑटो-फिल हो गया है!\n\n"
                        f"🚀 **मार्केटप्लेस बिक्री**: Dashboard पर 'Set Selected to Marketplace' दबाएं!"
                    )
                else:
                    bot_response = (
                        f"🌾 **Yield & Income Plan for {st_display} ({land_area} Hectares)**:\n\n"
                        f"1️⃣ **Recommended Crop**: {target_crop} (Alternative: {st_info['alt']})\n"
                        f"2️⃣ **Predicted Total Yield**: ~{total_yield_tons} Tons\n"
                        f"3️⃣ **Suggested Market Price**: ₹{price_per_ton:,} / Ton\n"
                        f"4️⃣ **Projected Gross Revenue**: ₹{total_revenue:,}\n"
                        f"5️⃣ **Dashboard Form**: Values auto-filled on your dashboard!\n\n"
                        f"🚀 **Marketplace Action**: Click 'Set Selected to Marketplace' on your Dashboard to post your crop!"
                    )

            elif any(w in msg_lower for w in ['hello', 'hi', 'namaste', 'hey', 'नमस्ते', 'हेलो']):
                if is_hindi:
                    bot_response = "नमस्ते! मैं एग्रीप्रेडिक्ट एआई सहायक हूँ। 🌾 आप पूछ सकते हैं: उपयोगकर्ता पंजीकरण (Registration), CNN फसल रोग पहचान (Disease Scan), या अपने राज्य का नाम बताएं!"
                else:
                    bot_response = "Hello! I am your AgriPredict AI Assistant. 🌾 Ask me about **User Registration**, **CNN Crop Disease Scanning**, or share your **State** for crop recommendations!"

            else:
                if is_hindi:
                    bot_response = "मैं आपकी मदद कर सकता हूँ! अपना राज्य बताएं (जैसे 'महाराष्ट्र') - मैं अनुशंसित फसल और मिट्टी के मानक मान बताऊंगा, फिर आपसे ज़मीन का आकार (हेक्टेयर) पूछूंगा!"
                else:
                    bot_response = "I am here to help! Tell me your State (e.g. 'Maharashtra') — I will recommend the best crop and ideal soil values, then ask for your land size to calculate your yield!"

    # Save to chat history
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO chat_history (user_id, user_message, bot_response) VALUES (?, ?, ?)',
            (user_id, user_message, bot_response)
        )
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"Chat history DB error: {db_err}")

    result = {'response': bot_response}
    if form_data:
        result['form_data'] = form_data

    return jsonify(result), 200


def setup_demo_jpg_images():
    """Create sample infected crop JPG images in static directory for demonstration."""
    import os
    try:
        from PIL import Image, ImageDraw
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        os.makedirs(static_dir, exist_ok=True)

        samples = {
            'leaf_blight_sample.jpg': {
                'bg': (34, 139, 34),
                'spots': [
                    ((60, 50, 180, 120), (139, 69, 19), (218, 165, 32)),
                    ((120, 160, 220, 240), (101, 67, 33), (255, 215, 0)),
                    ((40, 220, 140, 290), (139, 69, 19), (218, 165, 32))
                ]
            },
            'powdery_mildew_sample.jpg': {
                'bg': (46, 125, 50),
                'spots': [
                    ((50, 60, 150, 150), (240, 240, 240), (200, 200, 200)),
                    ((140, 130, 250, 230), (245, 245, 245), (210, 210, 210)),
                    ((70, 200, 180, 280), (235, 235, 235), (190, 190, 190))
                ]
            },
            'leaf_rust_sample.jpg': {
                'bg': (56, 142, 60),
                'spots': [
                    ((80, 40, 110, 70), (211, 84, 0), (230, 126, 34)),
                    ((150, 90, 180, 120), (211, 84, 0), (230, 126, 34)),
                    ((60, 140, 90, 170), (192, 57, 43), (230, 126, 34)),
                    ((130, 190, 160, 220), (211, 84, 0), (230, 126, 34)),
                    ((90, 240, 120, 270), (192, 57, 43), (230, 126, 34))
                ]
            }
        }

        for filename, data in samples.items():
            filepath = os.path.join(static_dir, filename)
            img = Image.new('RGB', (300, 300), color=data['bg'])
            draw = ImageDraw.Draw(img)

            # Draw leaf veins
            draw.line([(150, 0), (150, 300)], fill=(20, 90, 20), width=3)
            draw.line([(150, 50), (50, 100)], fill=(25, 100, 25), width=2)
            draw.line([(150, 100), (250, 150)], fill=(25, 100, 25), width=2)
            draw.line([(150, 180), (60, 230)], fill=(25, 100, 25), width=2)
            draw.line([(150, 230), (240, 280)], fill=(25, 100, 25), width=2)

            # Draw disease spots
            for box, inner_color, outer_color in data['spots']:
                draw.ellipse(box, fill=outer_color)
                x1, y1, x2, y2 = box
                margin = (x2 - x1) // 4
                inner_box = (x1 + margin, y1 + margin, x2 - margin, y2 - margin)
                draw.ellipse(inner_box, fill=inner_color)

            img.save(filepath, 'JPEG', quality=95)
            print(f"Generated dummy JPG sample: {filepath}")

    except Exception as e:
        print(f"Error creating dummy JPG images: {e}")

setup_demo_jpg_images()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
