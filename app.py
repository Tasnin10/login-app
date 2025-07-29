from flask import Flask, request, render_template_string, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key-123'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database table for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# HTML templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-container { max-width: 400px; margin: auto; }
        .error { color: red; }
        .success { color: green; }
        .form-group { margin-bottom: 15px; position: relative; }
        input, button { padding: 8px; width: 100%; box-sizing: border-box; }
        button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        a { text-decoration: none; color: #4CAF50; }
        .bi-eye, .bi-eye-slash { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer; font-size: 16px; }
        .password-container { position: relative; }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>Login</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <p class="{{ category }}">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST" action="{{ url_for('login') }}">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required value="{{ request.form.get('username', '') }}">
            </div>
            <div class="form-group password-container">
                <label>Password:</label>
                <input type="password" name="password" id="password" required value="{{ request.form.get('password', '') }}">
                <i class="bi bi-eye-slash" id="togglePassword"></i>
            </div>
            <button type="submit">Login</button>
        </form>
        <p><a href="{{ url_for('register') }}">Need an account? Register</a></p>
    </div>
    <script>
        const togglePassword = document.querySelector('#togglePassword');
        const password = document.querySelector('#password');
        togglePassword.addEventListener('click', function () {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.classList.toggle('bi-eye');
            this.classList.toggle('bi-eye-slash');
        });
    </script>
</body>
</html>
"""

REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-container { max-width: 400px; margin: auto; }
        .error { color: red; }
        .success { color: green; }
        .form-group { margin-bottom: 15px; position: relative; }
        input, button { padding: 8px; width: 100%; box-sizing: border-box; }
        button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        a { text-decoration: none; color: #4CAF50; }
        .bi-eye, .bi-eye-slash { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer; font-size: 16px; }
        .password-container { position: relative; }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>Register</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <p class="{{ category }}">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST" action="{{ url_for('register') }}">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required value="{{ request.form.get('username', '') }}">
            </div>
            <div class="form-group password-container">
                <label>Password:</label>
                <input type="password" name="password" id="password" required value="{{ request.form.get('password', '') }}">
                <i class="bi bi-eye-slash" id="togglePassword"></i>
            </div>
            <button type="submit">Register</button>
        </form>
        <p><a href="{{ url_for('login') }}">Already have an account? Login</a></p>
    </div>
    <script>
        const togglePassword = document.querySelector('#togglePassword');
        const password = document.querySelector('#password');
        togglePassword.addEventListener('click', function () {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.classList.toggle('bi-eye');
            this.classList.toggle('bi-eye-slash');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            flash('Login successful!', 'success')
            return render_template_string(LOGIN_TEMPLATE)
        else:
            flash('Invalid username or password.', 'error')
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        else:
            new_user = User(username=username, password=password)  # In production, hash passwords!
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template_string(REGISTER_TEMPLATE)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)