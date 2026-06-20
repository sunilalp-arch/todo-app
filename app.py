from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

USERS_FILE = 'users.json'

# ── Data helpers ──────────────────────────────────────────────

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# ── User class ────────────────────────────────────────────────

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    users = load_users()
    if username in users:
        return User(username)
    return None

# ── Routes ────────────────────────────────────────────────────

@app.route('/')
@login_required
def home():
    users = load_users()
    tasks = users[current_user.id]['tasks']
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task = request.form.get('task')
    if task:
        users = load_users()
        users[current_user.id]['tasks'].append(task)
        save_users(users)
    return redirect('/')

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    users = load_users()
    tasks = users[current_user.id]['tasks']
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_users(users)
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        users = load_users()
        if username in users:
            flash('Username already exists.', 'danger')
        elif len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
        elif len(password) < 4:
            flash('Password must be at least 4 characters.', 'danger')
        else:
            users[username] = {
                'password': generate_password_hash(password),
                'tasks': []
            }
            save_users(users)
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        users = load_users()
        if username in users and check_password_hash(users[username]['password'], password):
            login_user(User(username))
            return redirect('/')
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
