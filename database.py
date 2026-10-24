import sqlite3

DB_NAME = "agripredict.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Admin', 'Farmer', 'Vendor')),
        phone TEXT DEFAULT '',
        location TEXT DEFAULT '',
        requirements TEXT DEFAULT ''
    )
    """)
    
    # Create Listings table for the Marketplace
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        crop_name TEXT NOT NULL,
        quantity_tons REAL NOT NULL,
        price_per_ton REAL NOT NULL,
        status TEXT DEFAULT 'Available',
        FOREIGN KEY (farmer_id) REFERENCES users (id)
    )
    """)

    # Create Transactions table (CRM & Connectivity)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id INTEGER NOT NULL,
        vendor_id INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        total_price REAL NOT NULL,
        commission REAL DEFAULT 0,
        status TEXT DEFAULT 'Interested', -- Interested, ContactsShared, Finalized
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (listing_id) REFERENCES listings (id),
        FOREIGN KEY (vendor_id) REFERENCES users (id),
        FOREIGN KEY (farmer_id) REFERENCES users (id)
    )
    """)

    # Create Support Tickets table (CRM Strategy)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        category TEXT DEFAULT 'General',
        status TEXT DEFAULT 'Open',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Create Disease Logs table (CNN Crop Disease Classifier)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disease_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        image_filename TEXT NOT NULL,
        predicted_disease TEXT NOT NULL,
        confidence REAL NOT NULL,
        treatment_advice TEXT DEFAULT '',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Create Chat History table (LLM Platform Assistant)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_message TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully with new tables.")

# Utility Functions
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Return dicts instead of tuples
    return conn

if __name__ == "__main__":
    init_db()
