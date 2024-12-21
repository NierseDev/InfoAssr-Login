import secrets
import pyrebase
import mysql.connector
from flask import Flask, render_template, request, url_for, session, redirect
from flask_assets import Environment, Bundle


# ---------------------------------------------------------------------------------------------------------------------- #


# Database
def connectDB():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        database='test-login'
    )

    return db

# Firebase
config = {
    'apiKey': "AIzaSyDOAiIojcRjrvyLriKg_m-Wb3Qg81p4MUQ",
    'authDomain': "infoassr-accesscontrol.firebaseapp.com",
    'projectId': "infoassr-accesscontrol",
    'storageBucket': "infoassr-accesscontrol.firebasestorage.app",
    'messagingSenderId': "1006581544132",
    'appId': "1:1006581544132:web:50078cb289d6a8f1008591",
    'measurementId': "G-X9RZN36KG1",
    'databaseURL': ''
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


# ---------------------------------------------------------------------------------------------------------------------- #


# App
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


# ---------------------------------------------------------------------------------------------------------------------- #


# URL Routes:
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email

            return redirect(url_for('dashboard'))
        except:
            return render_template('login.html', message="Login Failed, Check Details!")
            
        
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')

        try:
            auth.create_user_with_email_and_password(email, password)
            message = "User registered successfully!"
            color = '#70fa70'
        except(Exception):
            message = "Error: Failed to Register User!"
            color = '#a81b1b'
        
        return render_template('registration.html', message=message, color=color)
    
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template("dashboard.html")

@app.route('/fetch_table_data')
def fetch_table_data():
    table_name = request.args.get('table_name')
    columns = []
    rows = []
    if table_name:
        connect = connectDB()
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM "+table_name)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        for row in result:
            rows.append(list(row))
        connect.close()

    return {'columns': columns, 'rows': rows}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

