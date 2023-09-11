from flask import Flask, render_template, redirect

app = Flask(__name__)

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

# FUNCTIONAL GATEWAYS...


if __name__ == '__main__':
    app.run()
