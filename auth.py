import bcrypt
from database import get_connection, log_action

def register_user(username, password, role="staff"):
    """
    Register a new user with a securely hashed password.
    
    Args:
        username (str): Chosen username.
        password (str): Plain text password (will be hashed).
        role (str): User role - 'admin', 'doctor', or 'staff'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Hash the password — NEVER store plain text passwords
    password_hash = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()
    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s);
        """, (username, password_hash, role))
        conn.commit()
        print(f"✅ User '{username}' registered successfully as {role}.")
    except Exception as e:
        print(f"❌ Error registering user: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def login(username, password):
    """
    Verify username and password against the database.
    
    Args:
        username (str): The username entered.
        password (str): The plain text password entered.
    
    Returns:
        dict: User info if login successful, None if failed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT password_hash, role FROM users WHERE username = %s;
    """, (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        print(f"✅ Login successful! Welcome, {username} ({result[1]})")
        log_action(username, "Logged into the EMR system")
        return {"username": username, "role": result[1]}
    else:
        print("❌ Invalid username or password.")
        return None

# Test registration and login when run directly
if __name__ == "__main__":
    print("Setting up test user...")
    register_user("admin", "Admin1234!", role="admin")
    print("\nTesting login...")
    user = login("admin", "Admin1234!")
    if user:
        print(f"Logged in as: {user['username']} | Role: {user['role']}")