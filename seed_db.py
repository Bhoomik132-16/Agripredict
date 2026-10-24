import sqlite3
from werkzeug.security import generate_password_hash
from database import init_db

def seed_data():
    init_db()
    conn = sqlite3.connect("agripredict.db")
    cursor = conn.cursor()

    # 1. Clear existing data
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM listings")
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM support_tickets")
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'listings', 'transactions', 'support_tickets')")
    except sqlite3.OperationalError:
        # sqlite_sequence might not exist if no AUTOINCREMENT has been used yet
        pass

    # 2. Add Admin
    cursor.execute("""
    INSERT INTO users (name, email, password, role, phone, location) 
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("Supreme Admin", "admin@agripredict.com", generate_password_hash("admin123"), "Admin", "+91 9999900000", "SCM Hub"))

    # 3. Add Farmers (Diversified locations)
    farmers = [
        ("Rajesh Kumar", "rajesh@farm.com", "farmer123", "Karnataka", "+91 8877665544"),
        ("Sohan Singh", "sohan@farm.com", "farmer123", "Punjab", "+91 7766554433"),
        ("Amit Das", "amit@farm.com", "farmer123", "Assam", "+91 9122334455"),
        ("Vikram Patil", "vikram@farm.com", "farmer123", "Maharashtra", "+91 8122334455"),
        ("Manoj Reddy", "manoj@farm.com", "farmer123", "Andhra Pradesh", "+91 7122334455")
    ]
    for name, email, pwd, loc, ph in farmers:
        cursor.execute("INSERT INTO users (name, email, password, role, phone, location) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, email, generate_password_hash(pwd), "Farmer", ph, loc))

    # 4. Add Vendors with Requirements
    vendors = [
        ("FreshFoods B2B", "fresh@vendor.com", "vendor123", "Bangalore", "Looking for 50T Rice and 20T Sugarcane weekly."),
        ("AgriCorp Export", "agri@vendor.com", "vendor123", "Mumbai", "Bulk requirement for high-grade Wheat (200T+).")
    ]
    for name, email, pwd, loc, req in vendors:
        cursor.execute("INSERT INTO users (name, email, password, role, phone, location, requirements) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (name, email, generate_password_hash(pwd), "Vendor", "+91 9000011111", loc, req))

    # 5. Add Seed Listings
    listings = [
        (2, "Rice", 50, 450),
        (3, "Wheat", 120, 380),
        (4, "Maize", 40, 290),
        (5, "Sugarcane", 200, 310),
        (6, "Cotton(lint)", 15, 800),
        (2, "Black pepper", 5, 1500),
        (3, "Soyabean", 60, 550),
        (4, "Barley", 30, 420),
        (5, "Potato", 45, 250),
        (6, "Jute", 100, 260),
        (2, "Onion", 25, 300),
        (3, "Garlic", 10, 800),
        (4, "Turmeric", 15, 950),
        (5, "Banana", 8, 120),
        (6, "Cashewnut", 12, 1100),
        (2, "Moong(Green Gram)", 18, 700)
    ]
    for f_id, crop, qty, price in listings:
        cursor.execute("INSERT INTO listings (farmer_id, crop_name, quantity_tons, price_per_ton) VALUES (?, ?, ?, ?)",
                       (f_id, crop, qty, price))

    # 6. Add some Mock Transactions
    txns = [
        (1, 7, 2, 22500, 6750, "Finalized"),
        (2, 8, 3, 45600, 0, "Paid_OrderPlaced"),
        (3, 7, 4, 11600, 0, "SCM_Managed"),
        (4, 7, 5, 62000, 0, "Paid_OrderPlaced"),
        (5, 8, 6, 12000, 0, "SCM_Managed")
    ]
    for l_id, v_id, f_id, price, comm, status in txns:
        cursor.execute("""
        INSERT INTO transactions (listing_id, vendor_id, farmer_id, total_price, commission, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (l_id, v_id, f_id, price, comm, status))

    # 7. Add Diverse Support Tickets for Pie Chart
    tickets = [
        (2, "Yield prediction showing error in Karnataka.", "Technical"),
        (3, "Payment status not updated after SCM.", "Billing"),
        (7, "Vendor app freezing on checkout.", "Technical"),
        (8, "Truck delayed for last shipment.", "Logistics"),
        (2, "Need more crop types in advisor.", "General")
    ]
    for u_id, msg, cat in tickets:
        cursor.execute("INSERT INTO support_tickets (user_id, message, category) VALUES (?, ?, ?)",
                       (u_id, msg, cat))

    conn.commit()
    conn.close()
    print("Database reset and seeded with professional ecosystem data.")

if __name__ == "__main__":
    seed_data()
