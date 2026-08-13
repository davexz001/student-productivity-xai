import bcrypt

# Mock secure database of users with roles
USER_DB = {
    "student1": {
        "password_hash": bcrypt.hashpw(b"student123", bcrypt.gensalt()).decode('utf-8'),
        "role": "Student"
    },
    "counselor1": {
        "password_hash": bcrypt.hashpw(b"counselor123", bcrypt.gensalt()).decode('utf-8'),
        "role": "Counselor"
    },
    "admin1": {
        "password_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8'),
        "role": "Admin"
    }
}

def verify_credentials(username, password):
    """Verifies username and password using secure bcrypt hashing."""
    if username in USER_DB:
        stored_hash = USER_DB[username]["password_hash"].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True, USER_DB[username]["role"]
    return False, None