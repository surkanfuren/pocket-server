from flask import Flask, render_template, redirect, request, session, url_for, abort
from flask_mail import Mail, Message
import sqlite3
import hashlib
import requests
from dotenv import load_dotenv
import os

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
    return render_template('pages/index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    message = None
    if request.method == "POST":
        print(request.form)
        secret_response = request.form.get('g-recaptcha-response', False)
        verify_response = requests.post(url=f'{VERIFY_URL}?secret={os.getenv("SECRET_KEY")}&response={secret_response}').json()
        if verify_response['success'] == False:
            abort(401)
        email = request.form["email"]
        password_first = request.form["password"]
        password = hash_password(password_first)
        cursor.execute("SELECT * FROM users WHERE user_mail =? AND user_pass =?", (email, password))
        user = cursor.fetchone()

        if user is None:
            message = "Wrong email or password. Please check your credentials."
            #No use of this now, saving for later use## session['login_attempts'] = session.get('login_attempts', 0) + 1

        else:
            session["logged_in"] = True
            session["id"] = user[0]
            session["email"] = user[1]
            #No use of this now, saving for later use## session.pop('login_attempts', None)
            return redirect(url_for('dashboard'))



    return render_template('pages/login.html', message=message,site_key=SITE_KEY)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    message = None
    emptyMessage = None
    if request.method == "POST":
        print(request.form)
        secret_response = request.form.get('g-recaptcha-response', False)
        verify_response = requests.post(url=f'{VERIFY_URL}?secret={os.getenv("SECRET_KEY")}&response={secret_response}').json()
        if verify_response['success'] == False:
            abort(401)
        email = request.form['email']
        password_first = request.form['password']
        password = hash_password(password_first)
        print(email)
        if is_email_used(email):
            message = "This email is already in use. Please choose another mail or log in to your account!"
        if (email == ''):
            emptyMessage = "Your e-mail can not be empty!"
        else:
            session["mail_in_use"] = False
            cursor.execute("INSERT INTO users(user_mail,user_pass) VALUES(?,?)", (email, password))
            conn.commit()
            return redirect("/login")

    return render_template('pages/signup.html', message=message,site_key=SITE_KEY, emptyMessage=emptyMessage)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        user_id = session["id"]
        email = session["email"]
        username = email.split("@")[0]

    # Product search

    if request.method == "POST":
        product = request.form['product']
        cursor.execute("INSERT INTO products (user_id, product_name) VALUES (?, ?)", (user_id, product))
        conn.commit()

    cursor.execute("SELECT product_name FROM products WHERE user_id = ?", (user_id,))
    products = cursor.fetchall()

    return render_template('pages/dashboard.html', username=username, products=products)

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
           print("Recovering password!")
            msg= Message("Hey",sender='noreply@demo.com',recipients=['berkayygemici@gmail.com'])
            msg.body="Hey how r u"
            mail.send(msg)
            return "Sent Email"
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


if __name__ == '__main__':
    app.run(debug=True)
