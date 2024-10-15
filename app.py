import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
import os

current_user = None

# Function to retrieve shop profile
def get_shop_profile():
    conn = sqlite3.connect('liquor_billing.db')
    c = conn.cursor()
    c.execute("SELECT shop_name, shop_address FROM profile LIMIT 1")
    profile = c.fetchone()
    conn.close()
    return profile if profile else ("Your Shop", "Address Not Set")

# Function to display shop info and login screen
def display_login_screen():
    shop_name, shop_address = get_shop_profile()
    
    login_window = tk.Toplevel(root)
    login_window.title(f"{shop_name}")
    
    # Display shop name and address
    tk.Label(login_window, text=f"Welcome to {shop_name}", font=("Merriweather", 18)).pack(pady=10)
    tk.Label(login_window, text=f"{shop_address}", font=("Merriweather", 14)).pack(pady=5)
    
    # Login form
    tk.Label(login_window, text="Username:").pack(pady=5)
    login_username = tk.Entry(login_window)
    login_username.pack(pady=5)

    tk.Label(login_window, text="Password:").pack(pady=5)
    login_password = tk.Entry(login_window, show="*")
    login_password.pack(pady=5)

    def attempt_login():
        username = login_username.get()
        password = login_password.get()

        conn = sqlite3.connect('liquor_billing.db')
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            global current_user
            current_user = user[0]
            messagebox.showinfo("Login Success", f"Welcome {current_user}!")
            login_window.destroy()
            tabs.pack(expand=1, fill="both")  # Show the rest of the tabs after login
        else:
            messagebox.showwarning("Login Failed", "Incorrect username or password.")

    tk.Button(login_window, text="Login", command=attempt_login).pack(pady=10)

# Function to add liquor stock
def add_liquor():
    name = liquor_name.get()
    category = liquor_category.get()
    price = liquor_price.get()
    quantity = liquor_quantity.get()
    image_path = liquor_image_path.get()

    if name and price and quantity and image_path:
        conn = sqlite3.connect('liquor_billing.db')
        c = conn.cursor()

        # Insert liquor into stock table
        c.execute("INSERT INTO stock (name, category, price, quantity, image_path) VALUES (?, ?, ?, ?, ?)",
                  (name, category, float(price), int(quantity), image_path))
        conn.commit()
        conn.close()

        # Clear input fields
        liquor_name.delete(0, tk.END)
        liquor_category.delete(0, tk.END)
        liquor_price.delete(0, tk.END)
        liquor_quantity.delete(0, tk.END)
        liquor_image_path.delete(0, tk.END)

        messagebox.showinfo("Success", "Liquor added to stock!")
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields and select an image.")

# Function to upload liquor image
def upload_image():
    filename = filedialog.askopenfilename(initialdir="/", title="Select Image",
                                          filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png")))
    liquor_image_path.insert(tk.END, filename)

# Function to save the shop profile
def save_profile():
    shop_name_value = shop_name.get()
    shop_address_value = shop_address.get()

    conn = sqlite3.connect('liquor_billing.db')
    c = conn.cursor()
    
    # Insert or update profile
    c.execute("INSERT OR REPLACE INTO profile (id, shop_name, shop_address) VALUES (1, ?, ?)", 
              (shop_name_value, shop_address_value))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Profile Saved", "Shop profile saved successfully!")

# Function to sell liquor
def sell_liquor():
    liquor_id = selected_liquor.get().split()[0]
    sell_quantity = sale_quantity.get()

    if liquor_id and sell_quantity and current_user:
        conn = sqlite3.connect('liquor_billing.db')
        c = conn.cursor()

        # Fetch current stock quantity
        c.execute("SELECT quantity FROM stock WHERE liquor_id=?", (liquor_id,))
        current_quantity = c.fetchone()

        if current_quantity is None:
            messagebox.showwarning("Stock Error", "Selected liquor does not exist.")
            return
        
        current_quantity = current_quantity[0]

        if int(sell_quantity) > current_quantity:
            messagebox.showwarning("Stock Error", "Out of Stock.")
        else:
            # Update stock
            new_quantity = current_quantity - int(sell_quantity)
            c.execute("UPDATE stock SET quantity=? WHERE liquor_id=?", (new_quantity, liquor_id))

            # Record transaction
            c.execute("INSERT INTO transactions (liquor_id, quantity, transaction_type, date, served_by) VALUES (?, ?, ?, ?, ?)",
                      (liquor_id, int(sell_quantity), "outflow", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_user))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Sale processed! Receipt generated.")
            generate_receipt(liquor_id, sell_quantity)
    else:
        messagebox.showwarning("Input Error", "Please select a liquor, enter quantity, and log in.")

# Function to generate and print receipt
def generate_receipt(liquor_id, quantity):
    shop_name, shop_address = get_shop_profile()
    conn = sqlite3.connect('liquor_billing.db')
    c = conn.cursor()
    c.execute("SELECT name, price FROM stock WHERE liquor_id=?", (liquor_id,))
    liquor = c.fetchone()
    conn.close()

    if liquor is None:
        messagebox.showwarning("Error", "Liquor not found for receipt generation.")
        return

    # Generate receipt
    total_price = float(liquor[1]) * int(quantity)
    receipt_text = f"""
    Shop Name: {shop_name}
    Address: {shop_address}
    ------------------------------------
    Item: {liquor[0]}
    Quantity: {quantity}
    Price per Unit: Ksh {liquor[1]:.2f}
    Total: Ksh {total_price:.2f}
    ------------------------------------
    Served by: {current_user}
    Thank you for shopping with us!
    """

    receipt_window = tk.Toplevel(root)
    receipt_window.title("Receipt")
    receipt_label = tk.Label(receipt_window, text=receipt_text, justify="left")
    receipt_label.pack()

    # Button to print the receipt
    tk.Button(receipt_window, text="Print Receipt", command=lambda: print_receipt(receipt_text)).pack(pady=10)

# Function to print receipt (stub)
def print_receipt(receipt_text):
    # Printing functionality is not implemented here; it could be handled with libraries like `win32print`
    messagebox.showinfo("Print Receipt", "Receipt printed successfully!")

# Function to load liquors for selling
def load_liquors():
    conn = sqlite3.connect('liquor_billing.db')
    c = conn.cursor()
    c.execute("SELECT liquor_id, name FROM stock")
    liquors = c.fetchall()
    conn.close()

    liquor_options = [f"{liquor[0]} - {liquor[1]}" for liquor in liquors]
    selected_liquor.set(liquor_options[0] if liquor_options else "")  # Set the default selection
    selected_liquor_menu['menu'].delete(0, 'end')  # Clear current options

    for option in liquor_options:
        selected_liquor_menu['menu'].add_command(label=option, command=lambda value=option: selected_liquor.set(value))

# Function to view stock
def view_stock():
    conn = sqlite3.connect('liquor_billing.db')
    c = conn.cursor()
    c.execute("SELECT name, category, price, quantity FROM stock")
    stocks = c.fetchall()
    conn.close()

    # Clear previous stock display
    for widget in stock_frame.winfo_children():
        widget.destroy()

    # Display stock
    tk.Label(stock_frame, text="Stock List:", font=("Arial", 14)).pack(pady=10)
    for stock in stocks:
        tk.Label(stock_frame, text=f"Name: {stock[0]}, Category: {stock[1]}, Price: Ksh {stock[2]:.2f}, Quantity: {stock[3]}").pack()

# GUI setup
root = tk.Tk()
root.title("Liquor Billing System")

# Hide tabs until login
tabs = ttk.Notebook(root)
tab1 = ttk.Frame(tabs)
tab2 = ttk.Frame(tabs)
tab3 = ttk.Frame(tabs)
tab4 = ttk.Frame(tabs)

tabs.add(tab2, text="Sell Liquor")
tabs.add(tab3, text="View Stock")
tabs.add(tab1, text="Add Liquor")
tabs.add(tab4, text="Profile Settings")

# Initially hide tabs until login
tabs.pack_forget()

# Call the login screen on launch
display_login_screen()

# Profiles Tab (Tab 4)
tk.Label(tab4, text="Shop Name:").grid(row=0, column=0, padx=5, pady=5)
shop_name = tk.Entry(tab4)
shop_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(tab4, text="Shop Address:").grid(row=1, column=0, padx=5, pady=5)
shop_address = tk.Entry(tab4)
shop_address.grid(row=1, column=1, padx=5, pady=5)

tk.Button(tab4, text="Save Profile", command=save_profile).grid(row=2, columnspan=2, pady=10)

# Add Liquor Tab (Tab 1)
tk.Label(tab1, text="Liquor Name:").pack(pady=5)
liquor_name = tk.Entry(tab1)
liquor_name.pack(pady=5)

tk.Label(tab1, text="Category:").pack(pady=5)
liquor_category = tk.Entry(tab1)
liquor_category.pack(pady=5)

tk.Label(tab1, text="Price:").pack(pady=5)
liquor_price = tk.Entry(tab1)
liquor_price.pack(pady=5)

tk.Label(tab1, text="Quantity:").pack(pady=5)
liquor_quantity = tk.Entry(tab1)
liquor_quantity.pack(pady=5)

tk.Label(tab1, text="Image Path:").pack(pady=5)
liquor_image_path = tk.Entry(tab1)
liquor_image_path.pack(pady=5)

tk.Button(tab1, text="Upload Image", command=upload_image).pack(pady=5)
tk.Button(tab1, text="Add Liquor", command=add_liquor).pack(pady=10)

# Sell Liquor Tab (Tab 2)
selected_liquor = tk.StringVar(tab2)
tk.Label(tab2, text="Select Liquor:").pack(pady=5)

# Create a menu for the dropdown
selected_liquor_menu = tk.OptionMenu(tab2, selected_liquor, "")
selected_liquor_menu.pack(pady=5)

tk.Label(tab2, text="Quantity to Sell:").pack(pady=5)
sale_quantity = tk.Entry(tab2)
sale_quantity.pack(pady=5)

tk.Button(tab2, text="Sell Liquor", command=sell_liquor).pack(pady=10)

# View Stock Tab (Tab 3)
stock_frame = tk.Frame(tab3)
stock_frame.pack(pady=10)
tk.Button(tab3, text="View Stock", command=view_stock).pack(pady=10)

# Load initial data
load_liquors()

# Create database tables if they don't exist
def create_tables():
    conn = sqlite3.connect('liquor_billing.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, shop_name TEXT, shop_address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stock (liquor_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price REAL, quantity INTEGER, image_path TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, liquor_id INTEGER, quantity INTEGER, transaction_type TEXT, date TEXT, served_by TEXT)''')
    conn.commit()
    conn.close()

create_tables()

# Start the GUI loop
root.mainloop()
