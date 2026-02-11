# 4. Message Length Analyzer
# Problem Statement:
# Analyze message sizes.
# messages = ["Hi", "Welcome to the platform", "OK"]

# Requirements:
# Print the length of each message
# Flag messages longer than 10 characters
# Real-World Application: Text filtering and validation systems


messages = ["Hi", "Welcome to the platform", "OK"]

print("Message Analysis:")
print("-" * 30)

for msg in messages:
    length = len(msg)
    
    if length > 10:
        status = "[FLAGGED: Too Long]"
    else:
        status = "[OK]"
        
    print(f"'{msg}' | Length: {length} {status}")