from flask import Flask, flash, render_template, request, session, redirect, g
from flask_wtf import FlaskForm
from wtforms import StringField,Form,TextField,TextAreaField, validators,SubmitField
from wtforms.validators import InputRequired
import hashlib
import mysql.connector as mariadb
import schedule
import time
import threading
import os

#User Class for global variable
class User:
    def __init__(self, id, username, firstname):
        self.id = id
        self.username = username
        self.firstname = firstname

    def __repr__(self):
        return f'<User: {self.username}>'

users = []

app = Flask(__name__)
app.secret_key = "12345"

#Check for session before each request, create global variable with logged in user for use with other pages on domain
@app.before_request
def before_request():
    g.user = None

    if 'user_ID' in session:
        for x in users:
            if x.id == session['user_ID']:
                g.user = x

#Home Page
@app.route('/')
def home():
    return render_template('home.html')

#Login Page
@app.route('/login', methods=['post', 'get'])
def login():
    error = None
    if(request.method=='POST'):

	#Remove session
        session.pop('user_ID', None)

	#Get username and password from POST request
        username = request.form.get('username')
        passwordEntry = request.form.get('password')

	#Hash password with SHA256 Algorithm
        entryPasswordHash = hashlib.sha256(passwordEntry.encode('utf-8')).hexdigest()

        try:
	    #Connect to DB
            conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
            cur = conn.cursor()

	    #Create SQL Query
            sql = "SELECT sesame, userID, first_name FROM SFMSUser WHERE username = %s"
            sqlVar = (username, )

	    #Run SQL Query and retrieve records
            cur.execute(sql, sqlVar)
            result = cur.fetchall()

            if not result:
                error = "Invalid Username"
                return render_template('login.html', error = error)

	    #Test for password match
            if result[0][0] == entryPasswordHash:

    	        #Create Session
                session['user_ID'] = result[0][1]
                users.append(User(result[0][1], username, result[0][2]))

                #Redirect to profile page
                return redirect('/SFMS/profile')

            error = "Invalid Password"
        except mariadb.Error as e:
            print(f"Error: {e}")

    return render_template('login.html', error = error)

#Booking Page
@app.route('/booking')
def booking():
    return render_template('booking.html')

#Profile Page
@app.route('/profile')
def profile():

    #Check if there is a user stored in global variable i.e. Someone is logged in
    if not g.user:
        return redirect('/SFMS/login')
    return render_template('profile.html')

#Base Page
@app.route('/base')
def base():
    return render_template('base.html')

#Header
@app.route('/header')
def header():
    return render_template('header.html')

#Footer
@app.route('/footer')
def footer():
    return render_template('footer.html')

#Error Pafe
@app.route('/errorpage')
def errorpage():
    return render_template('404.html')

#Run Server
if __name__ == "__main__":
    app.run(debug=True)

