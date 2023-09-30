from flask import Flask, render_template, redirect, request, session, url_for, abort
from flask_session import Session
from dotenv import load_dotenv
from datetime import timedelta
import requests
import hashlib
import sqlite3
import pymysql
import pyotp
import redis
import json
import os


app = Flask(__name__)
load_dotenv()


# App Configurations
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'fourthand-server-session'
# app.config['SESSION_REDIS'] = redis.from_url(os.environ['REDIS_URL'])  # Remote Redis (Heroku)
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)  # Local Redis
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
Session(app)


SITE_KEY = os.environ.get('SITE_KEY+')
VERIFY_URL = os.environ.get('VERIFY_URL')


# RDS MySQL Credentials
endpoint = os.environ.get('DB_ENDPOINT')
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
database = os.environ.get('DB_NAME')


# Database Connection
#conn = pymysql.connect(host=endpoint, user=username, password=password, port=3306, database=database)
#cursor = conn.cursor()



try:
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    print("Connection successful")
except sqlite3.Error as e:
    print(f"Connection error:{e}")
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()



# __________________________________________________ PAGE ROUTES __________________________________________________ #


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return render_template('pages/index.html')
@app.route('/tasks',methods=['GET','POST'])
def tasks():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        new_task = request.form['new_task']
        cursor.execute("INSERT INTO tasks (task_description,task_writer) VALUES (?, ?)", (new_task, session["id"]))
        conn.commit()
    return render_template('pages/tasks.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    session["logged_in"] = False
    session["id"] = None
    session["email"] = None
    session["phone_number"] = None
    message = None

    if request.method == "POST":
        print(request.form)
        secret_response = request.form.get('g-recaptcha-response', False)
        verify_response = requests.post(url=f'{VERIFY_URL}?secret={os.getenv("SECRET_KEY")}&response={secret_response}').json()

        if not verify_response['success']:
            abort(401)

        email = request.form["email"]
        password_first = request.form["password"]
        password = hash_password(password_first)
        cursor.execute("SELECT * FROM users WHERE user_mail = ? AND user_pass = ?", (email, password))
        user = cursor.fetchone()

        if user is None:
            message = "Wrong email or password. Please check your credentials."
            # No use of this now, saving for later use## session['login_attempts'] = session.get('login_attempts', 0) + 1

        else:
            session["logged_in"] = True
            session["id"] = user[0]
            session["email"] = user[1]
            session["phone_number"] = user[3]
            # No use of this now, saving for later use## session.pop('login_attempts', None)
            return redirect(url_for('dashboard'))

    return render_template('pages/login.html', message=message, site_key=SITE_KEY)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    message = None
    empty_message = None
    if request.method == "POST":
        print(request.form)
        secret_response = request.form.get('g-recaptcha-response', False)
        verify_response = requests.post(url=f'{VERIFY_URL}?secret={os.getenv("SECRET_KEY")}&response={secret_response}').json()
        if not verify_response['success']:
            abort(401)
        email = request.form['email']
        password_first = request.form['password']
        password = hash_password(password_first)
        print(email)
        print(is_email_used(email))
        if is_email_used(email):
            message = "This email is already in use. Please choose another email or log in to your account!"
        elif email == '':
            empty_message = "Your e-mail can not be empty!"
        else:
            session["mail_in_use"] = False
            cursor.execute("INSERT INTO users(user_mail,user_pass) VALUES(?, ?)", (email, password))
            conn.commit()
            return redirect("/login")

    return render_template('pages/signup.html', message=message, site_key=SITE_KEY, emptyMessage=empty_message)


@app.route('/delete_account', methods=['POST'])
def delete_account():
    account_to_delete = session["id"]
    try:
        cursor.execute("DELETE FROM users WHERE user_id=?", (account_to_delete,))
        conn.commit()
        session.clear()
        return "Account deletion successful", 200

    except Exception as err:
        print("HERE")
        conn.rollback()
        print(f"Error: {str(err)}")
        return "Account deletion failed", 500


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        user_id = session["id"]
        email = session["email"]
        # number = session["phone_number"]
        username = email.split("@")[0]
        session["username"] = username

    # Product search
    if request.method == "POST":
        product = request.form['product']
        cursor.execute("INSERT INTO products (user_id, product_name) VALUES (?, ?)", (user_id, product))
        conn.commit()

    cursor.execute("SELECT product_name FROM products WHERE user_id = ?", (user_id,))
    products = cursor.fetchall()

    return render_template('pages/dashboard.html', username=username, products=products)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    error_message = None
    success_message = None
    username = session["username"]
    if request.method == "POST":
        if "phone_change" in request.form:
            new_phone = request.form.get("phone_change")
            cursor.execute("UPDATE users SET phone_number =? WHERE user_id =?", (new_phone, session["id"]))
            conn.commit()
            session["phone_number"] = new_phone
            success_message = "Phone changed successfully"
        elif 'password_control_one' in request.form:
            control_one = request.form.get("password_control_one")
            control_two = request.form.get("password_control_two")
            if not is_strong_password(control_one):
                error_message = "Your password must be at least 6 characters"
            elif control_two != control_one:
                error_message = "The passwords you entered must match!"
            else:
                hashed_new_pass = hash_password(control_one)
                cursor.execute("UPDATE users SET user_pass=? WHERE user_id=?", (hashed_new_pass, session["id"]))
                conn.commit()
                success_message = "Password changed successfully"
    return render_template('pages/profile.html', username=username, number=session["phone_number"],
                           error_message=error_message, success_message=success_message)


@app.route('/about')
def about():
    return render_template('pages/about.html')


@app.route('/pricing')
def pricing():
    return render_template('pages/pricing.html')


@app.route('/faq')
def faq():
    return render_template('pages/faq.html')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    exist = False
    is_verified = False
    not_verified = None
    wrong_code = False
    message = None
    email = session["email"]
    extra_security = False
    success_message = session.get("success_message")

    secret_key = pyotp.random_base32()
    hotp = pyotp.HOTP(secret_key)

    verification_code = session.get("verification_code")
    typeof_code = None

    if request.method == "POST":
        if "g-recaptcha-response" in request.form:
            email = request.form["email"]
            cursor.execute("SELECT * FROM users WHERE user_mail = ?", (email,))
            user = cursor.fetchone()

            if user is None:
                message = "There are no users registered with this e-mail, try registering instead!"
            else:
                session["email"] = email
                exist = True
                print("Recovering password!")
                verification_code = hotp.at(0)
                session["verification_code"] = verification_code
                typeof_code = type(verification_code)
                print(f"Verification code: {verification_code}\n"
                      f"Type of verification code:{typeof_code}")

                # Lambda API Call
                func_endpoint = "https://njlzm7rsm9.execute-api.eu-north-1.amazonaws.com/default/forgotPasswordEmail"
                headers = {"Content-Type": "application/json"}

                # Sending mail to Lambda endpoint with POST request
                payload = {
                    "subject": "Fourthand password recovery",
                    "message_body": f"Your one-time password recovery code: {verification_code}",
                    "destination": [email]
                    }

                payload_json = json.dumps(payload)
                response = requests.post(func_endpoint, data=payload_json, headers=headers)

                # Receiving status response
                if response.status_code == 200:
                    print("Request successful!")
                    print("----------------------------------------------------------------------------------------------------")
                    print("Response:", response.text)
                    print("----------------------------------------------------------------------------------------------------")
                else:
                    print("Request failed. Status code:", response.status_code)
                    print("Response:", response.text)

        elif "codeSender" in request.form:
            input_code = request.form["code"]
            is_verified = verify(input_code, verification_code)
            print(f"Verification code: {verification_code}\n"
                  f"Type of verification code:{typeof_code}")
            print(f"User input: {input_code}")
            print(is_verified)
            print(type(input_code))

            if is_verified:
                print("Verification code is correct.")
                exist = False
                extra_security = True
            else:
                wrong_code = True
                exist = True
                not_verified = "Invalid code. Please check again."
                print(not_verified)

        elif "password_changed" in request.form:
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]
            hashed_new_password = hash_password(new_password)

            if new_password != confirm_password:
                print("Passwords do not match.")
            else:
                cursor.execute("UPDATE users SET user_pass = ? WHERE user_mail = ?", (hashed_new_password, email))
                conn.commit()
                success_message = "Password changed successfully."
                session["success_message"] = success_message
                return redirect(url_for('login'))

    return render_template('pages/forgot.html', message=message, pinCode=exist, is_verified=is_verified, wrong_code=wrong_code,
                           not_verified=not_verified, extra_security=extra_security, success_message=success_message)


# __________________________________________________ FUNCTIONAL ROUTES __________________________________________________ #


def is_email_used(email):
    cursor.execute("SELECT user_id FROM users WHERE user_mail=?", (email,))
    already_registered = cursor.fetchone()
    return already_registered is not None


def hash_password(passw):
    sha256 = hashlib.sha256()
    sha256.update(passw.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    return hashed_password


def verify(input_code, verification_code):
    is_verified = False
    if input_code == verification_code:
        is_verified = True
    return is_verified


@app.route('/logout')
def logout():
    if not session.get('logged_in'):
        abort(401)
    else:
        # session["logged_in"] = False
        session.clear()
        return redirect(url_for('login'))


def is_strong_password(passw):
    if len(passw) > 5:
        return True


if __name__ == '__main__':
    app.run(debug=True)
