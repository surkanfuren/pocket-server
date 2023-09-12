from flask import Flask, render_template, redirect, request
import sqlite3

app = Flask(__name__)
#conn = sqlite3.connect('database.db',check_same_thread=False)
try:
    conn = sqlite3.connect('database.db',check_same_thread=False)
    print("Connection succesfull")
except sqlite3.Error as e:
    print(f"Connection error:{e}")
cursor = conn.cursor()

# PAGE ROUTES

@app.route('/')
def index():
    return render_template('pages/index.html')

@app.route('/login')
def login():
    return render_template('pages/login.html')

@app.route('/signup')
def signup():
    return render_template('pages/signup.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/pricing')
def pricing():
    return render_template('pages/pricing.html')

@app.route('/faq')
def faq():
    return render_template('pages/faq.html')

@app.route('/sign-handler', methods=['POST'])
def signup_handler():
    email = request.form['email']
    password = request.form['password']
    if is_email_used(email):
        message = "This e-mail is already in use. Please choose another mail or log in to your account!"
        return render_template('pages/signup.html',message=message)
    else:
        cursor.execute("INSERT INTO users(user_mail,user_pass) VALUES(?,?)", (email, password))
        conn.commit()
    return redirect("/login")
@app.route('/login-handler', methods=['POST'])
def login_handler():
    email = request.form["email"]
    password = request.form["password"]
    cursor.execute("SELECT user_id FROM users where user_mail =? AND user_pass =?",(email,password))
    search = cursor.fetchone()
    #if search:

    return redirect("/")

# FUNCTIONAL GATEWAYS...
def is_email_used(email):
    cursor.execute("SELECT user_id FROM users WHERE user_mail=?",(email,))
    already_registered = cursor.fetchone()
    return already_registered is not None

if __name__ == '__main__':
    app.run(debug=True)
