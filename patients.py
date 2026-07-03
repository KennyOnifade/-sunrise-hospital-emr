from database import get_connection, log_action

def insert_patient(name, email, age, condition, current_user):
    """
    Insert a new patient into the database.
    
    Args:
        name (str): Patient full name.
        email (str): Patient email address.
        age (int): Patient age.
        condition (str): Medical condition.
        current_user (dict): Logged in user performing the action.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO patients (name, email, age, condition)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        """, (name.strip().title(), email.lower(), age, condition))
        conn.commit()
        log_action(current_user["username"], 
                  f"Added patient: {name}")
        print(f"✅ Patient '{name}' added successfully.")
    except Exception as e:
        print(f"❌ Error inserting patient: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_all_patients(current_user):
    """
    Retrieve all patients from the database.
    
    Args:
        current_user (dict): Logged in user performing the action.
    
    Returns:
        list: List of all patient records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, email, age, condition 
        FROM patients 
        ORDER BY name;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log_action(current_user["username"], "Viewed all patient records")
    return rows

def filter_patients_by_age(min_age, max_age, current_user):
    """
    Filter patients by age range.
    
    Args:
        min_age (int): Minimum age.
        max_age (int): Maximum age.
        current_user (dict): Logged in user performing the action.
    
    Returns:
        list: Filtered patient records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, email, age, condition 
        FROM patients
        WHERE age BETWEEN %s AND %s
        ORDER BY age;
    """, (min_age, max_age))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log_action(current_user["username"],
              f"Filtered patients by age {min_age}-{max_age}")
    return rows

def get_condition_counts(current_user):
    """
    Count patients per medical condition from real data.
    
    Args:
        current_user (dict): Logged in user performing the action.
    
    Returns:
        dict: Condition names and their patient counts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT condition, COUNT(*) as count
        FROM patients
        GROUP BY condition
        ORDER BY count DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log_action(current_user["username"], "Viewed condition analytics")
    return {row[0]: row[1] for row in rows}

def add_sample_patients(current_user):
    """
    Add realistic sample patients for demonstration.
    
    Args:
        current_user (dict): Logged in user performing the action.
    """
    sample_patients = [
        ("James Carter",    "james.carter@email.com",   45, "Hypertension"),
        ("Maria Lopez",     "maria.lopez@email.com",    32, "Diabetes"),
        ("Robert Johnson",  "robert.johnson@email.com", 58, "Hypertension"),
        ("Emily Davis",     "emily.davis@email.com",    27, "Flu"),
        ("Michael Brown",   "michael.brown@email.com",  61, "Diabetes"),
        ("Sarah Wilson",    "sarah.wilson@email.com",   39, "Hypertension"),
        ("David Martinez",  "david.martinez@email.com", 50, "Flu"),
        ("Jennifer Taylor", "jennifer.taylor@email.com",44, "Diabetes"),
        ("William Anderson","william.anderson@email.com",35,"Flu"),
        ("Linda Thomas",    "linda.thomas@email.com",   52, "Hypertension"),
    ]
    print("Adding sample patients...")
    for name, email, age, condition in sample_patients:
        insert_patient(name, email, age, condition, current_user)
    print("✅ Sample patients added successfully!")

# Test when run directly
if __name__ == "__main__":
    from auth import login
    # Login first before accessing patient data
    user = login("admin", "Admin1234!")
    if user:
        add_sample_patients(user)
        print("\nAll Patients:")
        patients = get_all_patients(user)
        for p in patients:
            print(f"  {p[0]} | {p[2]} yrs | {p[3]}")
        print("\nCondition Counts:")
        counts = get_condition_counts(user)
        for condition, count in counts.items():
            print(f"  {condition}: {count} patients")