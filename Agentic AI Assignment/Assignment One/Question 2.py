# 2. Pass / Fail Analyzer
# Problem Statement:
# Analyze student results.
# marks = [45, 78, 90, 33, 60]

# Requirements:
# A student passes if marks ≥ 50
# Count the total number of pass students
# Count the total number of fail students
# Print the final result clearly
# Real-World Application: Academic evaluation systems


# Input data
marks = [45, 78, 90, 33, 60]

# Initialize counters
pass_count = 0
fail_count = 0

# Iterate through the list
for score in marks:
    if score >= 50:
        pass_count += 1
    else:
        fail_count += 1

# Print the final result clearly
print("-" * 25)
print(f"Total Students: {len(marks)}")
print(f"Passed: {pass_count}")
print(f"Failed: {fail_count}")
print("-" * 25)
