from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('home.html')
# Set up a connection to your PostgreSQL database
conn = psycopg2.connect(database="expenses_tracker", user="postgres", password="860949", host="localhost", port="5432")

cur = conn.cursor()

# Define a User class
class User:
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password

# Define an Expense class
class Expense:
    def __init__(self, id, user_id, amount, category):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.category = category

# Rest of your code...

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if the email is already registered
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return "Email is already registered. Please use a different email."

        # Check if the username is already taken
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return "Username is already taken. Please choose a different username."

        # Create a new user
        cur.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", (email, username, password))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user exists
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        if user:
            return redirect(url_for('user_dashboard', username=username))
        else:
            return 'Invalid credentials. Please try again.'
    return render_template('login.html')

@app.route('/user/<username>/dashboard')
def user_dashboard(username):
    # Get user information
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_data = cur.fetchone()
    if user_data:
        user = User(user_data[0], user_data[1], user_data[2])
        # Get user expenses
        cur.execute("SELECT * FROM expenses WHERE user_id = %s", (username,))
        rows = cur.fetchall()
        expenses = [Expense(row[0], row[1], row[2], row[3]) for row in rows]
        return render_template('dashboard.html', user=user, expenses=expenses)
    else:
        return 'User not found.'

@app.route('/user/<username>/add_expense', methods=['POST'])
def add_expense(username):
    amount = float(request.form['amount'])
    category = request.form['category']
    # Add expense to database
    cur.execute("INSERT INTO expenses (user_id, amount, category) VALUES (%s, %s, %s)", (username, amount, category))
    conn.commit()
    return redirect(url_for('user_dashboard', username=username))

if __name__ == '__main__':
    app.run(debug=True)
