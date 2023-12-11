from flask import Flask, render_template, request, redirect, url_for,session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyodbc

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database setup
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=.;')
cursor = conn.cursor()

cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'C_table')
    CREATE TABLE C_table (
        id INT PRIMARY KEY IDENTITY(1,1),
        client_id NVARCHAR(255) NOT NULL,
        location NVARCHAR(255) NOT NULL,
        clientName NVARCHAR(255) NOT NULL,
        phone NVARCHAR(15) NOT NULL,
        anydesk NVARCHAR(255) NOT NULL,
        generatedPassword NVARCHAR(MAX) NOT NULL
    )
''')

conn.commit()

cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'login')
    CREATE TABLE login (
        id INT PRIMARY KEY IDENTITY(1,1),
        username NVARCHAR(255) NOT NULL,
        password NVARCHAR(255) NOT NULL
    )
''')
conn.commit()


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM login WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and user[2] == password:
            user_obj = User(user[0])  # Assuming the 'id' is in the first position
            login_user(user_obj)
            session["logged_in"] = True
            session["username"] = username
            return redirect("/index")  # Redirect to the dashboard after successful login
        if "logged_in" in session:
            return redirect("/index")  # If already logged in, redirect to the dashboard
        return render_template("login.html")
    else:
            return render_template('login.html', error='Invalid username or password')

# return render_template('index.html')


@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect('/login')


# @app.route('/index')
# def dashboard():
#     return render_template("index.html")

@app.route('/index')
def dashboard():
    if "logged_in" in session:
        return render_template("index.html")
    return redirect('/login')


@app.route('/post', methods=['POST'])
def post():
        client_id = request.form['client_id']
        location = request.form['location']
        clientName = request.form['clientName']
        phone = request.form['phone']
        anydesk = request.form['anydesk']
        generatedPassword = request.form['generatedPassword']

        cursor.execute('INSERT INTO C_table (client_id, location, clientName, phone, anydesk, generatedPassword) VALUES (?, ?, ?, ?, ?, ?)', (client_id, location, clientName, phone, anydesk, generatedPassword))
        conn.commit()


        return render_template('index.html')



@app.route('/signup')
def signup():
        return render_template('signup.html')

@app.route('/sign', methods=['POST'])
def sign():
        username = request.form['username']
        password = request.form['password']

        cursor.execute('INSERT INTO login (username, [password]) VALUES (?, ?)', (username, password))
        conn.commit()


        return render_template('login.html')


@app.route('/table')
def table():
    cursor.execute('SELECT * FROM C_table ORDER BY id DESC')
    data = cursor.fetchall()
    if "logged_in" in session:
            return render_template('table.html', data=data)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
