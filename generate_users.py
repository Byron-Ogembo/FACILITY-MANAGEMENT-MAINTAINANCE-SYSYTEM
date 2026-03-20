import os
import sys
import random
import string
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import execute_query, init_db
from app.utils.security import hash_password

def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_users():
    roles = {
        'Admin': 5,
        'Technician': 100,
        'Store Manager': 80,
        'Maintenance Manager': 80
    }
    
    users_list = []
    
    for role, count in roles.items():
        for i in range(1, count + 1):
            role_slug = role.lower().replace(' ', '')
            name = f"{role} {i}"
            email = f"{role_slug}{i}@cmms.com"
            password = generate_password()
            password_hash = hash_password(password)
            
            # Insert to DB
            execute_query(
                "INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (name, email, password_hash, role)
            )
            users_list.append([name, role, email, password])
            
    # Write to CSV
    csv_path = r"C:\Users\Jungle\.gemini\antigravity\brain\afcc61d5-c5ae-431b-a63c-c39c1b9ce833\generated_users.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Role', 'Email', 'Password'])
        writer.writerows(users_list)
        
    print(f"Generated {sum(roles.values())} users successfully.")
    print(f"List saved to {csv_path}")

if __name__ == '__main__':
    init_db()
    generate_users()
