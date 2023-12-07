# Starter Docs 📓

## Adding templates
Download the `templates` folder from [here](https://drive.google.com/file/d/1OWO6gnc2ml9vBlD7pVWhbIS6-crOC7Sd/view?usp=sharing) and add it to root directory.

## Using redis for session storage
```
pip install redis
```

start local redis server:

```
redis-server
```

For Heroku deploy: [Check out the documentation](https://devcenter.heroku.com/articles/heroku-redis)

## SQLite
[Download here](https://download.sqlitebrowser.org/DB.Browser.for.SQLite-3.12.2-win64.msi)

## Running Flask App
Run these commands in order:

`pip install Flask`

`export FLASK_DEBUG=1`

`flask run`

then visit http://127.0.0.1:5000

Here's the sign up form in `signup.html`:

You should specify the flask route which you send the `email` and `password` data here in form `'action'`:
```
<form method="POST" action="/your-flask-route">
  <div class="mb-3">
    <input type="email" placeholder="Your email address" class="form-control" id="email" name="email">
  </div>
  <div class="mb-3" style="margin-bottom: 10px;">
    <input type="password" placeholder="Create a new password" class="form-control" id="password" name="password">
  </div>
  <div class="d-flex justify-content-center">
    <button type="submit" class="btn btn-primary">Log in</button>
  </div>
</form>
```

And create the necessary route in flask (`app.py`)

Here's a simple route example for this case:
```
@app.route('/your-flask-route', methods=['POST'])
def signup_handler():
    email = request.form['email']
    password = request.form['password']
    
    # Now you can use the email and password variables for database queries here in route function
```

But first, create a database connection and cursor object outside the route functions:
```
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
```
### **Note**: if `database.db` file does not exist, `sqlite.connect()` function above will create one ⬆️

Now the cursor object is ready to use to make database queries. Don't forget to create table first! For example, we need a table named **`users`** with minimum of two **columns**: `email` and `password`. 

(You can create any table you need in a empty python file to make queries)

### **Remember**:
we need to make a return redirection to a specific page after the sign up proccess. It may be `login` route for example. Or an error page acording to the current status. So you should play around with `try-except` blocks and `if` conditions.

**Example scenario**: "This email address already in use!". What would you do in such a situation?


