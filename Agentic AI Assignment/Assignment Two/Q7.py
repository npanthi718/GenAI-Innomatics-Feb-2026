#Problem 7: Count Character Frequency

# Step 1: Initialize the input string
input_string = "python"

# Step 2: Create an empty dictionary to store counts
char_frequency = {}

# Step 3: Iterate through each character in the string
for char in input_string:
    if char in char_frequency:
        # If character exists, increment the value
        char_frequency[char] += 1
    else:
        # If character is new, initialize it with 1
        char_frequency[char] = 1

# Step 4: Display the result
print(char_frequency)