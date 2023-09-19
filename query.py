import sqlite3
import hashlib
import pyotp


secret_key = pyotp.random_base32()
hotp = pyotp.HOTP(secret_key)
verification_code = hotp.at(0)
print(verification_code)

input_code = input()
is_verified = hotp.verify(input_code, 0)
print(is_verified)
