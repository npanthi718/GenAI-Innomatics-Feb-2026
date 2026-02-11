# 1. User Login Check
# Problem Statement:
# Given a username and password, check whether login is successful.
# username = "admin"
# password = "1234"

# Requirements:
# Print "Login Successful" if both username and password match
# Otherwise print "Invalid Credentials"
# Real-World Application: Authentication systems


# Defined credentials
STORED_USER = "admin"
STORED_PASS = "1234"

# Getting input from the user
entered_user = input("Enter Username: ")
entered_pass = input("Enter Password: ")

# Logical Check
if entered_user == STORED_USER and entered_pass == STORED_PASS:
    print("Login Successful")
else:
    print("Invalid Credentials")
