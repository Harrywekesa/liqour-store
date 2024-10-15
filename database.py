import sqlite3

# Initialize and ensure database setup
def initialize_db():
    conn = sqlite3.connect('liquor_billing.db')
    c = conn.cursor()
    
    # Create stock table with the image_path column if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS stock (
        liquor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        quantity INTEGER,
        image_path TEXT
    )''')

    # Create profile table for storing shop info
    c.execute('''CREATE TABLE IF NOT EXISTS profile (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_name TEXT,
        shop_address TEXT,
        background_image TEXT
    )''')

    # Create transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        liquor_id INTEGER,
        quantity INTEGER,
        transaction_type TEXT,
        date TEXT,
        served_by TEXT
    )''')

    # Create users table for login
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')

    # Check if admin user exists, if not, create it
    c.execute("SELECT username FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))
        print("Default admin user created: username='admin', password='admin'")

    conn.commit()
    conn.close()

# Call this function at the beginning of your application
initialize_db()
