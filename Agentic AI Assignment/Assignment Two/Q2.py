# Problem 2: Highest Salary from Employee Data

# Step 1: Initialize the employee data dictionary
employees = {
    "Ravi": 75000,
    "Anita": 68000,
    "Kiran": 72000
}

# Step 2: Determine the employee with the highest salary
# max() with key=employees.get returns the key associated with the maximum value
highest_paid_employee = max(employees, key=employees.get)
highest_salary = employees[highest_paid_employee]

# Step 3: Print the results clearly
print(f"Employee with the highest salary: {highest_paid_employee}")
print(f"Salary: {highest_salary}")