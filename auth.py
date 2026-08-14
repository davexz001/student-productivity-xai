import sqlite3
import hashlib
import os

DB_NAME = "users.db"

def init_sqlite_db():
    """Initialize SQLite database with users table and seed default admin/counselor accounts."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    
    # Seed default Admin and Counselor accounts if DB is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_users = [
            ("admin", hash_password("admin123"), "Admin"),
            ("counselor", hash_password("counselor123"), "Counselor"),
            ("student1", hash_password("student123"), "Student")
        ]
        cursor.executemany("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", seed_users)
        conn.commit()
        
    conn.close()


def hash_password(password):
    """Generate SHA-256 hash of password."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(username, password):
    """Verify username and password against database."""
    init_sqlite_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    hashed_pwd = hash_password(password)
    cursor.execute("SELECT role FROM users WHERE username = ? AND password_hash = ?", (username, hashed_pwd))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return True, result[0]
    return False, None


def register_student(username, password):
    """Register a new student account (Public Registration restricted to Students)."""
    init_sqlite_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    hashed_pwd = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, hashed_pwd, "Student"))
        conn.commit()
        conn.close()
        return True, "Registration successful. You can now log in."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists."


def get_all_users():
    """Retrieve all users for Admin management view."""
    init_sqlite_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users