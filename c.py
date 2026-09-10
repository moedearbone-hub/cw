"""
Hostel Room Booking and Fees Management System

This program manages:
1. Hostel blocks and rooms
2. Student registration and room allocation
3. Fee payments
4. Student searching
5. Occupancy reports
6. Fee defaulters
7. Saving and loading data from a file
"""

import json
import os

# FILE USED TO SAVE DATA

DATA_FILE = "hostel_data.json"

# HOSTEL DATA SETUP

# Each hostel block has rooms.
# Each room has a capacity and current occupancy.

hostels = {
    "Block A": {
        "A101": {"capacity": 4, "occupancy": 0},
        "A102": {"capacity": 4, "occupancy": 0},
        "A103": {"capacity": 4, "occupancy": 0},
        "A104": {"capacity": 4, "occupancy": 0}
    },

    "Block B": {
        "B101": {"capacity": 3, "occupancy": 0},
        "B102": {"capacity": 3, "occupancy": 0},
        "B103": {"capacity": 3, "occupancy": 0},
        "B104": {"capacity": 3, "occupancy": 0}
    },

    "Block C": {
        "C101": {"capacity": 2, "occupancy": 0},
        "C102": {"capacity": 2, "occupancy": 0},
        "C103": {"capacity": 2, "occupancy": 0},
        "C104": {"capacity": 2, "occupancy": 0}
    }
}

# Dictionary used to store student information

students = {}

# DISPLAY OCCUPANCY OVERVIEW

def display_occupancy_overview():
    """Display a short occupancy overview when program starts."""

    print("\n==========================================")
    print("       HOSTEL OCCUPANCY OVERVIEW")
    print("==========================================")

    for block_name, rooms in hostels.items():

        total_capacity = 0
        total_occupied = 0

        for room in rooms.values():
            total_capacity += room["capacity"]
            total_occupied += room["occupancy"]

        print(
            f"{block_name}: "
            f"{total_occupied}/{total_capacity} occupied"
        )

# SAVE DATA

def save_data():
    """Save hostel and student information to a JSON file."""

    data = {
        "hostels": hostels,
        "students": students
    }

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print("\nData saved successfully.")

    except OSError as error:
        print("\nError saving data:", error)

# LOAD DATA

def load_data():
    """Load saved data when the program starts."""

    if not os.path.exists(DATA_FILE):
        print("\nNo previous data found.")
        print("Starting with new hostel data.")
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        loaded_hostels = data.get("hostels")
        if loaded_hostels is not None:
            hostels.clear()
            hostels.update(loaded_hostels)

        loaded_students = data.get("students")
        if loaded_students is not None:
            students.clear()
            students.update(loaded_students)

        print("\nPrevious data loaded successfully.")

    except (json.JSONDecodeError, OSError):
        print("\nThe saved data file is damaged or invalid.")
        print("Starting with new data instead.")

# GET VALID NUMBER

def get_positive_number(message):
    """Ask the user for a positive number."""

    while True:
        try:
            number = float(input(message))

            if number <= 0:
                print("Please enter a number greater than zero.")
            else:
                return number

        except ValueError:
            print("Invalid input. Please enter a number.")

# REGISTER STUDENT

def register_student():
    """Register a student and allocate a room."""

    print("\n==========================================")
    print("        STUDENT REGISTRATION")
    print("==========================================")

    registration_number = input(
        "Enter student registration number: "
    ).strip()

    if registration_number == "":
        print("Registration number cannot be empty.")
        return

    if registration_number in students:
        print("A student with that registration number already exists.")
        return

    name = input("Enter student name: ").strip()

    if name == "":
        print("Student name cannot be empty.")
        return

    # Display hostel blocks

    print("\nAvailable Hostel Blocks:")

    for block in hostels:
        print("-", block)

    block_name = input(
        "\nEnter hostel block: "
    ).strip()

    if block_name not in hostels:
        print("Invalid hostel block.")
        return

    # Display rooms in selected block

    print(f"\nRooms in {block_name}:")

    for room_number, room in hostels[block_name].items():

        available_space = (
            room["capacity"] - room["occupancy"]
        )

        print(
            f"{room_number} - "
            f"{room['occupancy']}/{room['capacity']} occupied "
            f"- {available_space} space(s) available"
        )

    room_number = input(
        "\nEnter room number: "
    ).strip()

    if room_number not in hostels[block_name]:
        print("Invalid room number.")
        return

    room = hostels[block_name][room_number]

    # Check whether room is full

    if room["occupancy"] >= room["capacity"]:
        print("\nROOM ALLOCATION REJECTED")
        print(
            f"Room {room_number} is already full."
        )
        return

    # Get total hostel fee

    total_fee = get_positive_number(
        "Enter total hostel fee: "
    )

    # Create student record

    students[registration_number] = {
        "name": name,
        "block": block_name,
        "room": room_number,
        "total_fee": total_fee,
        "amount_paid": 0,
        "payments": []
    }

    # Increase room occupancy

    room["occupancy"] += 1

    save_data()

    print("\nStudent registered successfully!")
    print("Name:", name)
    print("Registration Number:", registration_number)
    print("Hostel Block:", block_name)
    print("Room:", room_number)
    print("Outstanding Balance:", total_fee)

# RECORD FEE PAYMENT

def record_payment():
    """Record a full or partial payment."""

    print("\n==========================================")
    print("          FEE PAYMENT RECORDING")
    print("==========================================")

    registration_number = input(
        "Enter student registration number: "
    ).strip()

    if registration_number not in students:
        print("Student not found.")
        return

    student = students[registration_number]

    outstanding = (
        student["total_fee"] - student["amount_paid"]
    )

    print("\nStudent:", student["name"])
    print("Total Fee:", student["total_fee"])
    print("Amount Paid:", student["amount_paid"])
    print("Outstanding Balance:", outstanding)

    if outstanding <= 0:
        print("\nThis student's fees are already fully paid.")
        return

    while True:

        try:
            amount = float(
                input("Enter payment amount: ")
            )

            if amount <= 0:
                print("Payment must be greater than zero.")

            elif amount > outstanding:
                print(
                    "Payment cannot be greater than "
                    "the outstanding balance."
                )

            else:
                break

        except ValueError:
            print("Invalid amount. Enter a number.")

    # Update amount paid

    student["amount_paid"] += amount

    # Save individual payment

    student["payments"].append(amount)

    # Calculate new balance

    new_balance = (
        student["total_fee"] - student["amount_paid"]
    )

    save_data()

    print("\nPayment recorded successfully.")
    print("Payment Made:", amount)
    print("New Outstanding Balance:", new_balance)

# SEARCH STUDENT

def search_student():
    """Search for a student by name or registration number."""

    print("\n==========================================")
    print("             SEARCH STUDENT")
    print("==========================================")

    search_value = input(
        "Enter student name or registration number: "
    ).strip().lower()

    found = False

    for registration_number, student in students.items():

        name = student["name"].lower()

        if (
            search_value in name
            or search_value == registration_number.lower()
        ):

            balance = (
                student["total_fee"]
                - student["amount_paid"]
            )

            print("\n------------------------------------------")
            print("Student Name:", student["name"])
            print(
                "Registration Number:",
                registration_number
            )
            print("Hostel Block:", student["block"])
            print("Room:", student["room"])
            print("Total Fee:", student["total_fee"])
            print("Amount Paid:", student["amount_paid"])
            print("Outstanding:", balance)
            print("------------------------------------------")

            found = True

    if not found:
        print("\nNo student found.")

# OCCUPANCY REPORT

def occupancy_report():
    """Display a full occupancy report for each block."""

    print("\n==========================================")
    print("          HOSTEL OCCUPANCY REPORT")
    print("==========================================")

    for block_name, rooms in hostels.items():

        total_capacity = 0
        total_occupancy = 0

        print(f"\n{block_name}")
        print("------------------------------------------")

        for room_number, room in rooms.items():

            capacity = room["capacity"]
            occupancy = room["occupancy"]

            total_capacity += capacity
            total_occupancy += occupancy

            print(
                f"Room {room_number}: "
                f"{occupancy}/{capacity} occupied"
            )

        available = total_capacity - total_occupancy

        print(
            f"Total Occupied: "
            f"{total_occupancy}"
        )

        print(
            f"Total Capacity: "
            f"{total_capacity}"
        )

        print(
            f"Available Spaces: "
            f"{available}"
        )


# FEE DEFAULTERS


def fee_defaulters():
    """Display students whose balance is above a threshold."""

    print("\n==========================================")
    print("             FEE DEFAULTERS")
    print("==========================================")

    threshold = get_positive_number(
        "Enter outstanding balance threshold: "
    )

    found = False

    for registration_number, student in students.items():

        balance = (
            student["total_fee"]
            - student["amount_paid"]
        )

        if balance > threshold:

            print("\n------------------------------------------")
            print("Name:", student["name"])
            print(
                "Registration Number:",
                registration_number
            )
            print("Block:", student["block"])
            print("Room:", student["room"])
            print("Outstanding Balance:", balance)
            print("------------------------------------------")

            found = True

    if not found:
        print(
            "\nNo students found above "
            "the specified threshold."
        )

# VIEW ALL STUDENTS


def view_all_students():
    """Display all registered students."""

    print("\n==========================================")
    print("            ALL STUDENTS")
    print("==========================================")

    if len(students) == 0:
        print("No students have been registered.")
        return

    print(
        f"{'Reg No':<15}"
        f"{'Name':<20}"
        f"{'Block':<12}"
        f"{'Room':<10}"
        f"{'Balance':<10}"
    )

    print("-" * 67)

    for registration_number, student in students.items():

        balance = (
            student["total_fee"]
            - student["amount_paid"]
        )

        print(
            f"{registration_number:<15}"
            f"{student['name']:<20}"
            f"{student['block']:<12}"
            f"{student['room']:<10}"
            f"{balance:<10.2f}"
        )

# VIEW PAYMENT HISTORY


def payment_history():
    """Display payment history for a student."""

    print("\n==========================================")
    print("           PAYMENT HISTORY")
    print("==========================================")

    registration_number = input(
        "Enter registration number: "
    ).strip()

    if registration_number not in students:
        print("Student not found.")
        return

    student = students[registration_number]

    print("\nStudent:", student["name"])
    print("Registration Number:", registration_number)

    if len(student["payments"]) == 0:
        print("\nNo payments have been made.")
        return

    print("\nPayments:")

    total = 0

    for number, payment in enumerate(
        student["payments"],
        start=1
    ):

        print(
            f"{number}. {payment:.2f}"
        )

        total += payment

    print("\nTotal Paid:", total)

    balance = (
        student["total_fee"] - total
    )

    print("Outstanding Balance:", balance)


# MAIN MENU

def display_menu():
    """Display the main program menu."""

    print("\n")
    print("==========================================")
    print("   HOSTEL BOOKING & FEES MANAGEMENT")
    print("==========================================")

    print("1. Register student and allocate room")
    print("2. Record fee payment")
    print("3. Search for student")
    print("4. View occupancy report")
    print("5. View fee defaulters")
    print("6. View all students")
    print("7. View payment history")
    print("8. Save data")
    print("9. Exit")

    print("==========================================")

# MAIN PROGRAM


def main():
    """Main function that controls the program."""

    # Load previous data

    load_data()

    # Show occupancy when program starts

    display_occupancy_overview()

    # Keep showing menu until user exits

    while True:

        display_menu()

        choice = input(
            "Enter your choice (1-9): "
        ).strip()

        if choice == "1":
            register_student()

        elif choice == "2":
            record_payment()

        elif choice == "3":
            search_student()

        elif choice == "4":
            occupancy_report()

        elif choice == "5":
            fee_defaulters()

        elif choice == "6":
            view_all_students()

        elif choice == "7":
            payment_history()

        elif choice == "8":
            save_data()

        elif choice == "9":
            save_data()
            print("\nThank you for using the system.")
            print("Goodbye!")
            break

        else:
            print(
                "\nInvalid choice."
                " Please select a number from 1 to 9."
            )

# START THE PROGRAM

if __name__ == "__main__":
    main() 