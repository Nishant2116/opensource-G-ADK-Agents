import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_FILE = "demo.db"

def create_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create sales table
    cursor.execute('''

        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            region TEXT NOT NULL,
            amount INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            date DATE NOT NULL
        )
    ''')
    
    # Generate realistic sales data
    product_catalog = {
        'Electronics': [('Laptop', 1200), ('Monitor', 300), ('Webcam', 50)],
        'Accessories': [('Mouse', 25), ('Keyboard', 45), ('Headphones', 80), ('USB Hub', 20)],
        'Furniture': [('Desk Chair', 150)]
    }
    
    regions = ['North', 'South', 'East', 'West']
    
    sales_data = []
    base_date = datetime(2023, 1, 1)
    
    # Generate 150 records for better data density
    for _ in range(150):
        category = random.choice(list(product_catalog.keys()))
        prod, price = random.choice(product_catalog[category])
        region = random.choice(regions)
        
        # Add some price variation and calculate quantity
        unit_price = price + random.randint(-5, 5)
        quantity = random.randint(1, 5)
        total_amount = unit_price * quantity
        
        # Random date within 180 days
        day_offset = random.randint(0, 180)
        date_str = (base_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        
        sales_data.append((prod, category, region, total_amount, quantity, date_str))
        
    cursor.executemany("INSERT INTO sales (product, category, region, amount, quantity, date) VALUES (?, ?, ?, ?, ?, ?)", sales_data)

    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} created. Populated 'sales' table with {len(sales_data)} rows.")

if __name__ == "__main__":
    create_database()
