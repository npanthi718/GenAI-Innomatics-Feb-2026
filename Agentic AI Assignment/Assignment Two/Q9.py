#Problem 9: Check if a Key Exists in a Dictionary

# Step 1: Initialize the dictionary
employee_data = {
    "name": "Sushil",
    "role": "GenAI Intern",
    "id": "IN226018202"
}

# Step 2: Define the key we want to check
key_to_check = "name"

# Step 3: Use the 'in' keyword to check for existence
if key_to_check in employee_data:
    print("Employee exists")
else:
    print("Employee does not exist")