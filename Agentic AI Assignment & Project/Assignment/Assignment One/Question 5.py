# 5. Error Message Detector
# Problem Statement:
# Detect error messages from system logs.
# logs = ["INFO", "ERROR", "WARNING", "ERROR"]

# Requirements:
# Count the number of "ERROR" entries
# Print the total error count
# Real-World Application: Monitoring and log analysis systems


logs = ["INFO", "ERROR", "WARNING", "ERROR"]

# Initialize a counter
error_count = 0

# Scan the logs
for status in logs:
    if status == "ERROR":
        error_count += 1

# Output the result
print(f"Log Analysis Summary")
print("-" * 20)
print(f"Total ERROR entries found: {error_count}")