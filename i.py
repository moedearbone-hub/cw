"""Hostel room booking and fees management system.

The application deliberately keeps its data in simple dictionaries so it is
easy to understand, test, and persist as JSON for a small hostel office.
"""

import json
import os
from datetime import date


DATA_FILE = "Eden_hostel_data.json"


# ---------------------------------------------------------------------------
# PART 1 - DATA SETUP AND OCCUPANCY OVERVIEW
# Responsible area: hostel blocks, rooms, capacities, prices, and display.
# ---------------------------------------------------------------------------

def create_default_blocks():
	"""Return three blocks with fixed rooms, capacities, and room fees."""
	block_layout = {
		"Block A": (("101", 4, 250000), ("102", 4, 250000),
					("103", 4, 250000), ("104", 4, 250000)),
		"Block B": (("201", 3, 350000), ("202", 3, 350000),
					("203", 3, 350000)),
		"Block C": (("301", 2, 450000), ("302", 2, 450000)),
	}
	return {
		block_name: {
			"rooms": {
				room_number: {
					"capacity": capacity,
					"price": price,
					"occupants": [],
				}
				for room_number, capacity, price in rooms
			}
		}
		for block_name, rooms in block_layout.items()
	}


def print_occupancy_overview(hostel_blocks):
	"""Print block and room occupancy at startup or on request."""
	print("\nOCCUPANCY OVERVIEW")
	print("-" * 40)
	for block_name, block in hostel_blocks.items():
		occupied = sum(len(room["occupants"]) for room in block["rooms"].values())
		capacity = sum(room["capacity"] for room in block["rooms"].values())
		print(f"{block_name}: {occupied}/{capacity} beds occupied")
		for room_number, room in block["rooms"].items():
			places_left = room["capacity"] - len(room["occupants"])
			status = "[FULL]" if places_left == 0 else f"[{places_left} spot(s) left]"
			print(f"  Room {room_number}: {len(room['occupants'])}/{room['capacity']} {status}")
	print("-" * 40)
	print()


def find_block_of_room(hostel_blocks, room_number):
	"""Return the block containing a room, or None when it does not exist."""
	for block_name, block in hostel_blocks.items():
		if room_number in block["rooms"]:
			return block_name
	return None


# ---------------------------------------------------------------------------
# PART 2 - STUDENT REGISTRATION AND ROOM ALLOCATION
# Responsible area: room lookup, duplicate checks, capacity, and allocation.
# ---------------------------------------------------------------------------

def allocate_student(hostel_blocks, students, reg_no, name, room_number):
	"""Allocate a student using the fee attached to the selected room."""
	reg_no = reg_no.strip().upper()
	name = name.strip()
	room_number = room_number.strip()
	if not reg_no or not name:
		return False, "Registration number and student name are required."
	if reg_no in students:
		return False, "A student with that registration number already exists."
	block_name = find_block_of_room(hostel_blocks, room_number)
	if block_name is None:
		return False, f"Room {room_number} does not exist."

	room = hostel_blocks[block_name]["rooms"][room_number]
	if len(room["occupants"]) >= room["capacity"]:
		return False, f"Room {room_number} is already full."

	# Update the student record and room together so occupancy stays consistent.
	students[reg_no] = {
		"name": name,
		"block": block_name,
		"room": room_number,
		"total_fee": room["price"],
		"amount_paid": 0,
		"payment_history": [],
	}
	room["occupants"].append(reg_no)
	return True, f"{name} was allocated to {block_name}, room {room_number}."


# ---------------------------------------------------------------------------
# PART 3 - FEE PAYMENTS AND BALANCE CALCULATION
# Responsible area: payments, payment history, balances, and overpayment rules.
# ---------------------------------------------------------------------------

def record_payment(students, reg_no, amount):
	"""Record a full or partial payment without allowing overpayment."""
	reg_no = reg_no.strip().upper()
	if reg_no not in students:
		return False, "No student was found with that registration number."
	if amount <= 0:
		return False, "Payment amount must be greater than zero."

	student = students[reg_no]
	outstanding = get_balance(student)
	if amount > outstanding:
		return False, f"Payment exceeds the outstanding balance of {outstanding:.2f}."

	student["amount_paid"] += amount
	student["payment_history"].append({
		"date": date.today().isoformat(),
		"amount": amount,
	})
	return True, f"Payment recorded. New balance: {get_balance(student):.2f}."


def get_balance(student):
	"""Calculate the outstanding fee balance from the recorded totals."""
	# Calculate the value instead of storing it, preventing stale balances.
	return max(0, student["total_fee"] - student["amount_paid"])


# ---------------------------------------------------------------------------
# PART 4 - SEARCH AND REPORTING
# Responsible area: student search, occupancy reports, and fee defaulters.
# ---------------------------------------------------------------------------

def search_student(students, query):
	"""Find students by registration number or case-insensitive name."""
	query = query.strip().lower()
	return [
		(reg_no, student)
		for reg_no, student in students.items()
		if query in reg_no.lower() or query in student["name"].lower()
	]


def generate_occupancy_report(hostel_blocks):
	"""Return a full occupancy report for all blocks and rooms."""
	lines = ["Full occupancy report", "=" * 30]
	for block_name, block in hostel_blocks.items():
		rooms = block["rooms"]
		occupied = sum(len(room["occupants"]) for room in rooms.values())
		capacity = sum(room["capacity"] for room in rooms.values())
		lines.append(f"{block_name}: {occupied}/{capacity} beds occupied")
		for room_number, room in rooms.items():
			occupants = ", ".join(room["occupants"]) or "Empty"
			lines.append(
				f"  Room {room_number}: {len(room['occupants'])}/{room['capacity']} - {occupants}"
			)
	return "\n".join(lines)


def get_defaulters(students, threshold):
	"""Return students whose outstanding balance is above the threshold."""
	# A student exactly at the threshold is not included: the rule is balance > threshold.
	return [
		(reg_no, student, get_balance(student))
		for reg_no, student in students.items()
		if get_balance(student) > threshold
	]


# ---------------------------------------------------------------------------
# PART 5 - FILE PERSISTENCE AND DATA VALIDATION
# Responsible area: JSON storage, validation, missing files, and recovery.
# ---------------------------------------------------------------------------

def _is_valid_data(data):
	"""Check that loaded JSON contains usable blocks and student records."""
	if not isinstance(data, dict):
		return False
	blocks = data.get("blocks")
	students = data.get("students")
	if not isinstance(blocks, dict) or not isinstance(students, dict):
		return False
	for block in blocks.values():
		if not isinstance(block, dict) or not isinstance(block.get("rooms"), dict):
			return False
		for room in block["rooms"].values():
			if (
				not isinstance(room, dict)
				or not isinstance(room.get("capacity"), int)
				or room["capacity"] <= 0
				or not isinstance(room.get("price"), (int, float))
				or not isinstance(room.get("occupants"), list)
			):
				return False
	return True


def save_data(hostel_blocks, students, filepath=DATA_FILE):
	"""Save all records, reporting an error instead of terminating the app."""
	data = {"blocks": hostel_blocks, "students": students}
	try:
		with open(filepath, "w", encoding="utf-8") as file:
			json.dump(data, file, indent=2)
		return True, f"Data saved to {filepath}."
	except (OSError, TypeError) as error:
		return False, f"Could not save data: {error}"


def load_data(filepath=DATA_FILE):
	"""Load saved records, falling back to a clean layout if necessary."""
	if not os.path.exists(filepath):
		# Create the persistence file on the first run so future launches use the same data.
		blocks, students = create_default_blocks(), {}
		save_data(blocks, students, filepath)
		return blocks, students
	try:
		with open(filepath, "r", encoding="utf-8") as file:
			data = json.load(file)
		if not _is_valid_data(data):
			raise ValueError("unexpected data structure")
		return data["blocks"], data["students"]
	except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
		print(f"Warning: saved data could not be loaded ({error}). Starting with empty data.")
		# Replace damaged data immediately, rather than leaving the same error for the next run.
		blocks, students = create_default_blocks(), {}
		save_data(blocks, students, filepath)
		return blocks, students


# ---------------------------------------------------------------------------
# PART 6 - INPUT VALIDATION AND MENU DRIVER
# Responsible area: safe user input, menu actions, and program entry point.
# ---------------------------------------------------------------------------

def _read_non_empty(prompt):
	while True:
		value = input(prompt).strip()
		if value:
			return value
		print("This value cannot be empty.")


def _read_money(prompt, allow_zero=False):
	while True:
		try:
			value = float(input(prompt).strip())
			if value < 0 or (value == 0 and not allow_zero):
				raise ValueError
			return round(value, 2)
		except ValueError:
			minimum = "zero or more" if allow_zero else "greater than zero"
			print(f"Enter a valid amount ({minimum}).")


def _show_search_results(results):
	if not results:
		print("No matching students found.")
		return
	for reg_no, student in results:
		print(
			f"{reg_no} | {student['name']} | {student['block']} {student['room']} | "
			f"Balance: {get_balance(student):.2f}"
		)


def run_menu(hostel_blocks, students, filepath=DATA_FILE):
	"""Run the interactive warden menu until the user chooses exit."""
	while True:
		print("""
Hostel Management System
1. Register student and allocate room
2. Record fee payment
3. Search student
4. View occupancy report
5. View fee defaulters
6. Save data
7. Save and exit""")
		choice = input("Choose an option: ").strip()

		if choice == "1":
			reg_no = _read_non_empty("Registration number: ")
			name = _read_non_empty("Student name: ")
			print("Available rooms: " + ", ".join(
				room_number
				for block in hostel_blocks.values()
				for room_number in block["rooms"]
			))
			room_number = _read_non_empty("Room number: ")
			success, message = allocate_student(hostel_blocks, students, reg_no, name, room_number)
			print(message)
			if success:
				save_data(hostel_blocks, students, filepath)
		elif choice == "2":
			reg_no = _read_non_empty("Registration number: ")
			amount = _read_money("Payment amount: ")
			success, message = record_payment(students, reg_no, amount)
			print(message)
			if success:
				save_data(hostel_blocks, students, filepath)
		elif choice == "3":
			_show_search_results(search_student(students, _read_non_empty("Name or registration number: ")))
		elif choice == "4":
			print(generate_occupancy_report(hostel_blocks))
		elif choice == "5":
			threshold = _read_money("Show balances above: ", allow_zero=True)
			defaulters = get_defaulters(students, threshold)
			if not defaulters:
				print("No fee defaulters found.")
			else:
				for reg_no, student, balance in defaulters:
					print(f"{reg_no} | {student['name']} | Outstanding: {balance:.2f}")
		elif choice == "6":
			print(save_data(hostel_blocks, students, filepath)[1])
		elif choice == "7":
			print(save_data(hostel_blocks, students, filepath)[1])
			print("Goodbye.")
			return
		else:
			print("Invalid option. Please choose a number from the menu.")


def main():
	hostel_blocks, students = load_data()
	print_occupancy_overview(hostel_blocks)
	run_menu(hostel_blocks, students)


if __name__ == "__main__":
	main()