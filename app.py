from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://fmu76a694pv7tx5b:igvaouje2t8tcxgd@yhrz9vns005e0734.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/q8b1v3rybj8kvaiu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model for database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password, password):
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Incorrect username or password.", "danger")
    
    return render_template('login.html')

# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash("Username or Email already exists.", "danger")
            return redirect(url_for('signup'))
        
        # Hash the password and save new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Initialize database tables
    with app.app_context():
        db.create_all()
        
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
