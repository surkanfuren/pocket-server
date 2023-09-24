import sqlite3
import hashlib
import pyotp


"""
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent,"client-secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


app.config['MAIL_SERVER'] = 'smtp.elasticemail.com'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'fourthandel@smtp.com'
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASS")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
"""


secret_key = pyotp.random_base32()
hotp = pyotp.HOTP(secret_key)
verification_code = hotp.at(0)
print(verification_code)

input_code = input()
is_verified = hotp.verify(input_code, 0)
print(is_verified)
