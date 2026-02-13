# Problem 4: Count Products Above a Price Threshold

# Input list of product prices
prices = [450, 1200, 899, 1500, 300]

# Step 1: Initialize the counter
count = 0

# Step 2: Use a loop to compare each price with the threshold (1000)
for price in prices:
    if price > 1000:
        count += 1

# Step 3: Print the expected output
print(f"Products above 1000: {count}")