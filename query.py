import sqlite3
import hashlib

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    return hashed_password


email = "furkan@mail.com"
password_first = "furkan"
password = hash_password(password_first)

cursor.execute("SELECT * FROM users WHERE user_mail =? AND user_pass =?", (email, password))
user = cursor.fetchone()

print(user[1].split("@")[0])
print(user[3])

cursor.execute("SELECT product_name FROM products WHERE user_id = ?", (11,))
payload = cursor.fetchall()

for i in payload:
    print(i[0])


cursor.execute("SELECT * FROM users")
getit = cursor.fetchall()

for i in getit:
    print(i)
