# pip install bcrypt
import bcrypt

# The password to hash
password = b"my_secure_password"

# Generate a salt and hash the password
# The cost factor is specified in the gensalt function
salt = bcrypt.gensalt(rounds=12)
hashed_password = bcrypt.hashpw(password, salt)

print(hashed_password)



def verify_pw(password, hashed_pw):
    print("password:", password)
    print("hashed_pw:", hashed_pw)
    return bcrypt.checkpw(password, hashed_pw)


print("match?", verify_pw(b"my_secure_password", hashed_password))

h2 = '$2b$12$gkhJOzsZ5sMTwq8bedjq4eORde13RPZi3xU4HWd3iEk/xeSQua8WC'

print("match2", verify_pw(b"my_secure_password",b'$2b$12$gkhJOzsZ5sMTwq8bedjq4eORde13RPZi3xU4HWd3iEk/xeSQua8WC'))