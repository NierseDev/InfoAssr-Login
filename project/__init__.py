# PACKAGES
from flask import Flask, render_template, request, url_for, session, redirect
from flask_assets import Environment, Bundle

# Database
import mysql.connector

# Security
import hashlib
import secrets
from functools import wraps

app = Flask(__name__)
assets = Environment(app)

# Create Bundle for Flask-Assets to compile and prefix SCSS/SASS to CSS
css = Bundle('src/sass/main.sass',
             filters=['libsass'],
             output='dist/css/styles.css',
             depends='src/sass/*.sass')

assets.register("asset_css", css)
css.build()

# Secret Key
app.secret_key = secrets.token_urlsafe(16)

# Database
def connectDB():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        database='adet'
    )

    return db

# URL Routes:
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')
        password = hashlib.sha256(password.encode()).hexdigest()

        conn = connectDB()
        cur = conn.cursor()
        cur.execute("SELECT UserID, Email, HASHEDPassword, Status FROM adet_user WHERE Email = %s AND HASHEDPassword = %s", (email, password)) #LIMIT 1
        user = cur.fetchone()
        
        if user:
            if user[3] in ['Banned', 'Deleted']:
                return render_template('login.html', message="Account is Deleted or Banned")
            else:
                session['UserID'] = user[0]
                session['Email'] = user[1]
                return redirect(url_for('dashboard')), 301
        else:
            return render_template('login.html', message="Login Failed, Check Details!")
        
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')
        password = hashlib.sha256(password.encode()).hexdigest()
        fName = request.form.get('FirstName')
        lName = request.form.get('LastName')
        contactNum = request.form.get('ContactNum')
        address = request.form.get('Address')

        try:
            conn = connectDB()
            cursor = conn.cursor()

            query = "INSERT INTO adet_user (Email, HASHEDPassword, FirstName, LastName, ContactNum, Address) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (email, password, fName, lName, contactNum, address)

            cursor.execute(query, values)
            conn.commit()

            message = "User registered successfully!"
            color = '#70fa70'
        except(Exception):
            message = "Error: Failed to Register User!"
            color = '#a81b1b'
        finally:
            cursor.close()
            conn.close()
        
        return render_template('registration.html', message=message, color=color)
    
@app.route('/dashboard')
def dashboard():
    if 'UserID' not in session:
        return redirect(url_for('login'))
    
    if request.args.get('logout') == 'True':
        session.clear()
        return redirect(url_for('home'))
    
    conn = connectDB()
    cur = conn.cursor()
    cur.execute("SELECT Email, FirstName, LastName, ContactNum, Address FROM adet_user WHERE UserID = %s", (session['UserID'],))
    user = cur.fetchone()
    
    return render_template("dashboard.html", Email=user[0], FirstName=user[1], LastName=user[2], ContactNum=user[3], Address=user[4])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

