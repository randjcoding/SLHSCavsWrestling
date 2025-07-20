#!/usr/bin/env python3
"""
Temporary script to generate password hashes for database insertion
"""

from werkzeug.security import generate_password_hash

# User passwords
users = [
    {
        'email': 'joe_71@yahoo.com',
        'password': 'SR71brd!!',
        'first_name': 'Joe',
        'last_name': 'DiFede'
    },
    {
        'email': 'Hilldeontae1996@gmail.com', 
        'password': 'Password123$%^',
        'first_name': 'Donnie',
        'last_name': 'Hill'
    }
]

print("=== PASSWORD HASHES FOR DATABASE ===\n")

for user in users:
    hash_value = generate_password_hash(user['password'])
    print(f"User: {user['first_name']} {user['last_name']}")
    print(f"Email: {user['email']}")
    print(f"Password: {user['password']}")
    print(f"Hash: {hash_value}")
    print("-" * 50)

print("\n=== INSERT STATEMENTS ===\n")

for user in users:
    hash_value = generate_password_hash(user['password'])
    
    insert_sql = f"""INSERT INTO users (email, password_hash, first_name, last_name, role, created_at, modified_at, active) 
VALUES ('{user['email']}', '{hash_value}', '{user['first_name']}', '{user['last_name']}', 'admin', NOW(), NOW(), TRUE);"""
    
    print(insert_sql)
    print()

print("=== COPY THESE STATEMENTS TO YOUR DROPLET ===") 