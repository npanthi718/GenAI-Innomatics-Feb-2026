#Problem 5: Calculate Attendance Percentage

# Input list
attendance = ["P", "P", "A", "P", "P"]

# Step 1: Count the number of 'P' (Present) values
present_count = attendance.count("P")

# Step 2: Get the total number of days
total_days = len(attendance)

# Step 3: Calculate the percentage
# Formula: (Part / Total) * 100
attendance_percentage = (present_count / total_days) * 100

# Step 4: Display the result
print(f"Attendance Percentage: {attendance_percentage}")