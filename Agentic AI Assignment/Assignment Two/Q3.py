#Problem 3: Find Maximum and Minimum Values

# Input list
numbers = [45, 22, 89, 10, 66]
# Step 1: Initialize max and min with the first element
maximum = numbers[0]
minimum = numbers[0]

# Step 2: Use a loop to compare each element
for num in numbers:
    # Check for maximum
    if num > maximum:
        maximum = num
    
    # Check for minimum
    if num < minimum:
        minimum = num

# Step 3: Print the final results
print(f"List: {numbers}")
print(f"Max: {maximum}")
print(f"Min: {minimum}")