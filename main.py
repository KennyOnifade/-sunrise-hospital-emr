import pandas as pd
import matplotlib.pyplot as plt
from auth import login, register_user
from patients import (get_all_patients, filter_patients_by_age,
                     get_condition_counts, insert_patient)
from database import log_action

def get_age_range():
    """
    Get age range from user with input validation.

    Returns:
        tuple: (min_age, max_age) as integers.
    """
    while True:
        try:
            min_age = int(input("Enter minimum age: "))
            max_age = int(input("Enter maximum age: "))
            if min_age < 0 or max_age < min_age:
                print("❌ Invalid range. Minimum age must be"
                      " >= 0 and less than maximum age.")
                continue
            return min_age, max_age
        except ValueError:
            print("❌ Please enter valid numeric ages.")

def visualize_data(condition_counts, patients, filtered=False):
    """
    Create visualizations from real database data.

    Args:
        condition_counts (dict): Real condition data from database.
        patients (list): List of patient records.
        filtered (bool): Whether data is filtered by age.
    """
    if not condition_counts:
        print("❌ No data to visualize.")
        return

    # Bar chart of conditions
    plt.figure(figsize=(8, 6))
    plt.bar(condition_counts.keys(),
            condition_counts.values(), color="skyblue")
    plt.xlabel("Conditions")
    plt.ylabel("Number of Patients")
    plt.title("Prevalence of Conditions in EMR Data")
    plt.tight_layout()
    plt.savefig("conditions_plot.png")
    plt.show()

    # Pie chart of conditions
    plt.figure(figsize=(8, 6))
    plt.pie(condition_counts.values(),
            labels=condition_counts.keys(),
            autopct="%1.1f%%",
            colors=["lightblue", "lightgreen", "lightcoral"])
    plt.title("Distribution of Conditions in EMR Data")
    plt.tight_layout()
    plt.savefig("conditions_pie.png")
    plt.show()

    # Age histogram from real patient data
    ages = [p[2] for p in patients]
    plt.figure(figsize=(8, 6))
    plt.hist(ages, bins=5, color="lightcoral", edgecolor="black")
    plt.xlabel("Age")
    plt.ylabel("Number of Patients")
    plt.title("Age Distribution of " +
              ("Filtered Patients" if filtered else "All Patients"))
    plt.tight_layout()
    filename = ("filtered_age_distribution.png"
                if filtered else "age_distribution.png")
    plt.savefig(filename)
    plt.show()
    print("✅ Visualizations saved and displayed!")

def add_new_patient(current_user):
    """
    Prompt user to enter a new patient's details.

    Args:
        current_user (dict): Logged in user.
    """
    print("\n--- Add New Patient ---")
    name = input("Patient full name: ")
    email = input("Patient email: ")
    while True:
        try:
            age = int(input("Patient age: "))
            if age < 0:
                print("❌ Age cannot be negative.")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid age.")
    condition = input("Medical condition: ")
    insert_patient(name, email, age, condition, current_user)

def main():
    """Main EMR system with login and full menu."""
    print("\n" + "="*45)
    print("   Welcome to Sunrise Hospital EMR System")
    print("="*45)

    # --- LOGIN REQUIRED BEFORE ANYTHING ELSE ---
    current_user = None
    attempts = 0
    while current_user is None:
        if attempts >= 3:
            print("❌ Too many failed attempts. Exiting.")
            return
        print("\nPlease log in to continue.")
        username = input("Username: ")
        password = input("Password: ")
        current_user = login(username, password)
        if current_user is None:
            attempts += 1
            remaining = 3 - attempts
            if remaining > 0:
                print(f"  {remaining} attempt(s) remaining.")

    # --- MAIN MENU ---
    while True:
        print("\n" + "-"*45)
        print(f"  Logged in as: {current_user['username']}"
              f" ({current_user['role']})")
        print("-"*45)
        print("1. View all patients")
        print("2. Filter patients by age range")
        print("3. Add a new patient")
        print("4. View analysis and visualizations")
        print("5. Exit")
        print("-"*45)
        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            patients = get_all_patients(current_user)
            if patients:
                print(f"\n{'Name':<25}{'Email':<30}"
                      f"{'Age':<6}{'Condition'}")
                print("-"*75)
                for p in patients:
                    print(f"{p[0]:<25}{p[1]:<30}"
                          f"{p[2]:<6}{p[3]}")
            else:
                print("No patients found in the database.")

        elif choice == "2":
            min_age, max_age = get_age_range()
            patients = filter_patients_by_age(
                min_age, max_age, current_user)
            if patients:
                print(f"\nPatients aged {min_age}-{max_age}:")
                print(f"{'Name':<25}{'Age':<6}{'Condition'}")
                print("-"*45)
                for p in patients:
                    print(f"{p[0]:<25}{p[2]:<6}{p[3]}")
            else:
                print(f"No patients found between"
                      f" ages {min_age} and {max_age}.")

        elif choice == "3":
            add_new_patient(current_user)

        elif choice == "4":
            patients = get_all_patients(current_user)
            condition_counts = get_condition_counts(current_user)
            if not patients:
                print("No data available to analyze.")
                continue

            mean_age = sum(p[2] for p in patients) / len(patients)
            print("\n--- Analysis Results ---")
            print(f"Total Patients : {len(patients)}")
            print(f"Mean Age       : {mean_age:.1f} years")
            print("Condition Breakdown:")
            for condition, count in condition_counts.items():
                print(f"  {condition}: {count} patients")

            # Recommendation based on real data
            top = max(condition_counts.items(),
                      key=lambda x: x[1],
                      default=("None", 0))
            if top[1] > 3:
                print(f"\n⚠️  Recommendation: Focus resources on"
                      f" {top[0]} — affecting {top[1]} patients.")
            else:
                print("\n✅ Recommendation:"
                      " Continue monitoring condition trends.")

            visualize_data(condition_counts, patients)
            log_action(current_user["username"],
                      "Viewed full analysis and visualizations")

        elif choice == "5":
            log_action(current_user["username"],
                      "Logged out of the EMR system")
            print("\nGoodbye! Stay safe. 👋")
            break

        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()