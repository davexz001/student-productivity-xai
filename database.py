import sqlite3
import hashlib

DB_NAME = "edusphere.db"

def init_db():
    """Initializes SQLite tables for users and assessment history."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # User Credentials Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Historical Student Assessments Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            g1 REAL,
            g2 REAL,
            predicted_g3 REAL,
            risk_tier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Pre-populate default accounts if table is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        default_users = [
            ("student1", hash_password("password123"), "Student"),
            ("counselor1", hash_password("counselor123"), "Counselor"),
            ("admin1", hash_password("admin123"), "Admin")
        ]
        c.executemany("INSERT INTO users VALUES (?, ?, ?)", default_users)
        
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Standard SHA-256 password hashing helper."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, role="Student"):
    """Registers a new account into the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hash_password(password), role))
        conn.commit()
        conn.close()
        return True, "Account registered successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists."

def authenticate_user(username, password):
    """Verifies login credentials from SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    record = c.fetchone()
    conn.close()
    
    if record and record[0] == hash_password(password):
        return True, record[1]
    return False, None

def save_assessment(username, g1, g2, pred, risk):
    """Saves student evaluation to historical tracking logs."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO assessments (username, g1, g2, predicted_g3, risk_tier) VALUES (?, ?, ?, ?, ?)",
        (username, g1, g2, pred, risk)
    )
    conn.commit()
    conn.close()