from models import User


new_user = User.create("testuser", "testpassword")


if new_user:
    print("User created successfully:", new_user.username)
else:
    print("Failed to create user. Check MySQL connection.")
