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
            amount INTEGER NOT NULL,
            date DATE NOT NULL
        )
    ''')
    
    # Generate realistic sales data
    products = [
        ('Laptop', 1200), ('Mouse', 25), ('Keyboard', 45), 
        ('Monitor', 300), ('Headphones', 80), ('Webcam', 50),
        ('Desk Chair', 150), ('USB Hub', 20)
    ]
    
    sales_data = []
    base_date = datetime(2023, 1, 1)
    
    # Generate 60 records
    for _ in range(60):
        prod, price = random.choice(products)
        # Add some price variation
        actual_price = price + random.randint(-5, 5)
        # Random date within 90 days
        day_offset = random.randint(0, 90)
        date_str = (base_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        
        sales_data.append((prod, actual_price, date_str))
        
    cursor.executemany("INSERT INTO sales (product, amount, date) VALUES (?, ?, ?)", sales_data)

    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} created. Populated 'sales' table with {len(sales_data)} rows.")

if __name__ == "__main__":
    create_database()
