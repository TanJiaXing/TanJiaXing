import bcrypt

password = input("Enter password: ")
hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

print ("Original Password: " ,password)
print ("Hashed Password: ", hashed_password)

password_to_check = input("Enter password to checK: ")
if bcrypt.checkpw(password_to_check.encode('utf8'), hashed_password):
    print ("Match")
else:
    print ("No Match")
