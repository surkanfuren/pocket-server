from flask import Flask, render_template, redirect, request, session, url_for, abort
from flask_mail import Mail
import sqlite3
import hashlib
import requests
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)

load_dotenv()

app.secret_key = 'BAD_SECRET_KEY'
SITE_KEY = '6LfiYiEoAAAAAHojsCOY72WzNTGbFjZKIYFdhGPW'
VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
app.config['MAIL_SERVER'] = 'smtp.elasticemail.com'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'fourthandel@smtp.com'
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASS")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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
        cursor.execute("SELECT * FROM users WHERE user_mail =? AND user_pass =?", (email, password))
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
        if is_email_used(email):
            message = "This email is already in use. Please choose another email or log in to your account!"
        if email == '':
            empty_message = "Your e-mail can not be empty!"
        else:
            session["mail_in_use"] = False
            cursor.execute("INSERT INTO users(user_mail,user_pass) VALUES(?,?)", (email, password))
            conn.commit()
            return redirect("/login")

    return render_template('pages/signup.html', message=message, site_key=SITE_KEY, emptyMessage=empty_message)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        user_id = session["id"]
        email = session["email"]
        number = session["phone_number"]
        username = email.split("@")[0]
        session["username"] = username

    # Product search
    if request.method == "POST":
        product = request.form['product']
        cursor.execute("INSERT INTO products (user_id, product_name) VALUES (?, ?)", (user_id, product))
        conn.commit()

    cursor.execute("SELECT product_name FROM products WHERE user_id = ?", (user_id,))
    products = cursor.fetchall()

    return render_template('pages/dashboard.html', username=username, number=number, products=products)

@app.route('/phone_number')
def phone_number():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    username = session["username"]
    number = session["phone_number"]

    return render_template('pages/phone_number.html', username=username, number=number)

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

    message = None
    if request.method == "POST":
        email = request.form["email"]
        cursor.execute("SELECT * FROM users WHERE user_mail =?", (email,))
        user = cursor.fetchone()
        if user is None:
            message = "There are no users registered with this e-mail, try registering instead!"
        else:
            username = email.split("@")[0]
            print("Recovering password!")

            # Lambda API Call
            endpoint = "https://njlzm7rsm9.execute-api.eu-north-1.amazonaws.com/default/forgotPasswordEmail"
            headers = {"Content-Type": "application/json"}

            # Sending mail data to endpoint with POST request
            payload = {"subject": "Fourthand password recovery", "message_body": f"Dear {username}, we'll save your password soon!", "destination": [email]}
            payload_json = json.dumps(payload)
            response = requests.post(endpoint, data=payload_json, headers=headers)

            # Receiving response status
            if response.status_code == 200:
                print("Request successful!")
                print("----------------------------------------------------------------------------------------------------")
                print("Response:", response.text)
                print("----------------------------------------------------------------------------------------------------")
            else:
                print("Request failed. Status code:", response.status_code)
                print("Response:", response.text)

    return render_template('pages/forgot.html', message=message)

# __________________________________________________ FUNCTIONAL ROUTES __________________________________________________ #

def is_email_used(email):
    cursor.execute("SELECT user_id FROM users WHERE user_mail=?", (email,))
    already_registered = cursor.fetchone()
    return already_registered is not None

def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    return hashed_password

@app.route('/logout')
def logout():
    if not session.get('logged_in'):
        abort(401)
    else:
        session["logged_in"] = False
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
