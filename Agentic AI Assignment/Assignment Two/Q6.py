#Problem 6: Remove Duplicate Phone Numbers

# Input list of phone numbers (contains duplicates)
phone_numbers = [9876543210, 9123456789, 9876543210]

# Step 1: Use a set to filter out duplicates
# Sets only store unique values by definition
unique_numbers = set(phone_numbers)

# Step 2: Display the result
print(f"Unique phone numbers: {unique_numbers}")