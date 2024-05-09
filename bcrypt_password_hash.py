# pip install bcrypt
import bcrypt

# The password to hash
password = b"super_secure_password55557234_monkey_elephant_dog+bridhege"

# Generate a salt and hash the password
# The cost factor is specified in the gensalt function
salt = bcrypt.gensalt(rounds=12)
hashed_password = bcrypt.hashpw(password, salt)

print(hashed_password)

print(hashed_password)



print("Salt:", salt)
print("Hashed password:", hashed_password)


# Now let's check the password against the hash
check_password = password  # This should be the password you want to check
if bcrypt.checkpw(check_password, hashed_password):
    print("Password is correct")
else:
    print("Password is incorrect")