"""
Setup script to create a sample SQLite database with realistic data.
This creates a simple e-commerce database with customers, products, and orders.
"""

import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "shop.db"


def setup_database():
    """Create and populate the sample database."""
    print("=" * 60)
    print("DATABASE SETUP")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables if they exist
    print("\n[STEP 1] Dropping existing tables (if any)...")
    cursor.execute("DROP TABLE IF EXISTS order_items")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS customers")
    print("  ✓ Tables dropped")

    # Create tables
    print("\n[STEP 2] Creating tables...")

    # Customers table
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            city TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ Created 'customers' table")

    # Products table
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)
    print("  ✓ Created 'products' table")

    # Orders table
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    print("  ✓ Created 'orders' table")

    # Order items table (junction table for orders and products)
    cursor.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    print("  ✓ Created 'order_items' table")

    # Insert sample data
    print("\n[STEP 3] Inserting sample data...")

    # Customers
    customers = [
        ("Alice Johnson", "alice@email.com", "New York"),
        ("Bob Smith", "bob@email.com", "Los Angeles"),
        ("Carol Williams", "carol@email.com", "Chicago"),
        ("David Brown", "david@email.com", "Houston"),
        ("Eva Martinez", "eva@email.com", "Phoenix"),
    ]
    cursor.executemany(
        "INSERT INTO customers (name, email, city) VALUES (?, ?, ?)",
        customers
    )
    print(f"  ✓ Inserted {len(customers)} customers")

    # Products
    products = [
        ("Laptop", "Electronics", 999.99, 50),
        ("Mouse", "Electronics", 29.99, 200),
        ("Keyboard", "Electronics", 79.99, 150),
        ("Monitor", "Electronics", 349.99, 75),
        ("Desk Chair", "Furniture", 249.99, 30),
        ("Standing Desk", "Furniture", 499.99, 20),
        ("Notebook", "Office Supplies", 4.99, 500),
        ("Pen Set", "Office Supplies", 12.99, 300),
        ("Headphones", "Electronics", 149.99, 100),
        ("Webcam", "Electronics", 89.99, 80),
    ]
    cursor.executemany(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        products
    )
    print(f"  ✓ Inserted {len(products)} products")

    # Orders (with varied dates)
    base_date = datetime.now() - timedelta(days=30)
    orders_data = []
    statuses = ["pending", "shipped", "delivered", "delivered", "delivered"]

    for i in range(15):
        customer_id = random.randint(1, 5)
        order_date = (base_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        status = random.choice(statuses)
        orders_data.append((customer_id, order_date, status))

    cursor.executemany(
        "INSERT INTO orders (customer_id, order_date, status) VALUES (?, ?, ?)",
        orders_data
    )
    print(f"  ✓ Inserted {len(orders_data)} orders")

    # Order items
    order_items_data = []
    for order_id in range(1, 16):
        # Each order has 1-4 items
        num_items = random.randint(1, 4)
        used_products = set()
        for _ in range(num_items):
            product_id = random.randint(1, 10)
            while product_id in used_products:
                product_id = random.randint(1, 10)
            used_products.add(product_id)

            quantity = random.randint(1, 3)
            # Get the product price
            cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            unit_price = cursor.fetchone()[0]
            order_items_data.append((order_id, product_id, quantity, unit_price))

    cursor.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        order_items_data
    )
    print(f"  ✓ Inserted {len(order_items_data)} order items")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("DATABASE SETUP COMPLETE")
    print(f"Database file: {DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    setup_database()
