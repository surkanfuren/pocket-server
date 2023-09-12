from flask import Flask, render_template, redirect, request, session, url_for
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

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
    message = None
    if request.method == "POST":
        email = request.form["email"]
        password_first = request.form["password"]
        password = hash_password(password_first)

        cursor.execute("SELECT * FROM users WHERE user_mail =? AND user_pass =?", (email, password))
        user = cursor.fetchone()

        if user is None:
            message = "Wrong email or password. Please check your credentials."
            session["logged_in"] = False
        else:
            session["logged_in"] = True
            session["id"] = user[0]
            session["email"] = user[1]
            return redirect(url_for('dashboard'))

    return render_template('pages/login.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = None
    if request.method == "POST":
        email = request.form['email']
        password_first = request.form['password']
        password = hash_password(password_first)
        if is_email_used(email):
            message = "This email is already in use. Please choose another mail or log in to your account!"
        else:
            session["mail_in_use"] = False
            cursor.execute("INSERT INTO users(user_mail,user_pass) VALUES(?,?)", (email, password))
            conn.commit()
            return redirect("/login")

    return render_template('pages/signup.html', message=message)

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
