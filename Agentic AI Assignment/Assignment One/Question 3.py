# 3. Simple Data Cleaner
# Problem Statement:
# Clean and standardize user names.
# names = [" Alice ", "bob", " CHARLIE "]

# Requirements:
# Remove extra spaces
# Convert all names to lowercase
# Print the cleaned list
# Real-World Application: Data preprocessing before analysis


names = [" Alice ", "bob", " CHARLIE "]

# Clean: .strip() removes spaces, .lower() standardizes case
cleaned_names = [name.strip().lower() for name in names]

print("Cleaned List:", cleaned_names)