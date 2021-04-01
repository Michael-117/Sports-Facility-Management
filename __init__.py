from flask import Flask, flash, render_template, request, session, redirect, g,url_for
import flask
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,Form,TextField,TextAreaField, validators,SubmitField
from wtforms.validators import ValidationError,EqualTo,InputRequired
import datetime
import hashlib
import mysql.connector as mariadb
import schedule
import threading
import os
from flask_login import current_user,login_user,login_required

def timeLeft(nowTime: str, endTime: str):
    nowVals = nowTime.split(":")
    endVals = endTime.split(":")
    hrsDiff = int(endVals[0]) - int(nowVals[0])
    minsDiff = int(endVals[1]) - int(nowVals[1]) + 10
    secDiff = int(endVals[2]) - int(nowVals[2])

    secsLeft = (hrsDiff*3600) + (minsDiff*60) + (secDiff)
    return secsLeft

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
    error = ""
    if(request.method=='post'):

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
            sql = "SELECT sesame, userID, firstName FROM SFMSUser WHERE username = %s"
            sqlVar = (username, )

	    #Run SQL Query and retrieve records
            cur.execute(sql, sqlVar)
            result = cur.fetchall()

            if not result:
                error1 = "Invalid Username"
                flash(error1, "success")
                return render_template('login.html')

	    #Test for password match
            if result[0][0] == entryPasswordHash:

    	        #Create Session
                session['user_ID'] = result[0][1]
                users.append(User(result[0][1], username, result[0][2]))
                cur.close()
                conn.close()

                #Redirect to profile page
                return redirect('/SFMS/profile')

            error = "Invalid Password"
        except mariadb.Error as e:
            print(f"Error: {e}")

    flash(error, "success")
    return render_template('login.html')

@app.route('/adduser',methods=['get','post'])
@login_required
class adduserForm(FlaskForm):
    firstname=StringField('First Name', validators=[InputRequired()])
    lastname=StringField('Last Name', validators=[InputRequired()])
    username=StringField('Username', validators=[InputRequired()])
    usertype=StringField('User type', validators=[InputRequired()])
    useraddress=StringField('User address', validators=[InputRequired()])
    useremail=StringField('User email', validators=[InputRequired()])
    telephone=StringField('Telephone', validators=[InputRequired()])
    submit=SubmitField('Register')
    def validate_username(self,username):
        user=User.query.filter_by(username=self.username.data).first()
        if user is not None: #username exist
            raise ValidationError('Please use a different username.')
    
    def adduser():
        if not current_user.is_autheticated:
            flash('Please Login in as admin to add user')
            return redirect(url_for('login'))
        if current_user.username!='jbrown123':
            flash('Please Log in as admin to add user')
            return redirect(url_for('home'))
        form=adduserForm()
        if form.validate_on_submit():
            user=User(username=form.username.input,fullname=form.fullname.input)
            user.set_password(form.password.input)
            session.add(user)

        return render_template('adduser.html',title='Add User',form=form)

#Booking Page
@app.route('/booking', methods=['post', 'get'])
@login_required
def booking():
    if not g.user:
        return redirect('/SFMS/login')
    message = ""

    #Retrieve POST Request Data
    if (request.method == 'POST'):
        facility = request.form.get('facility')
        resource = request.form.get('resource')
        date = request.form.get('date')
        startTime = request.form.get('startTime')
        endTime = request.form.get('endTime')

        try:
            #Connect to DB
            conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
            cur = conn.cursor()

	    #Create SQL Query
            sql = "INSERT INTO Booking (facility, resource, useStart, useEnd, useDate, userID) VALUES (%s, %s, %s, %s, %s, %s)"
            sqlVar = (facility, resource, startTime, endTime, date, g.user.id )

	    #Run SQL Query
            cur.execute(sql, sqlVar)
            conn.commit()
            cur.close()
            conn.close()

        except mariadb.Error as e:
            print(f"Error: {e}")
    message = "Booking Created Successfully"
    flash(message, "success")
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

#Error Page
@app.route('/errorpage')
def errorpage():
    return render_template('404.html')

#Verify Booking
@app.route('/verify', methods=['post', 'get'])
@login_required
def verifyBooking():

    message = ""
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.today().time()

    if (request.method == 'POST'):
        name = request.form.get('sensor')
        facility = request.form.get('facility')
        rfid = request.form.get('rfid')

        try:
	    #Connect to DB
            conn = mariadb.connect(user="esp32", password="esp_boss5", host="localhost", database="SFM")
            cur = conn.cursor()

	    #Create SQL Query to log a facility access attempt
            sql = "INSERT INTO SensorData (sensor, facility, rfid) VALUES (%s, %s, %s)"
            sqlVar = (name, facility, rfid)

	    #Run SQL Query
            cur.execute(sql, sqlVar)
            conn.commit()

            #Create SQL Query to check for a booking
            sql = "SELECT resource, useStart, useEnd FROM Booking WHERE userID = (SELECT userID FROM Member WHERE cardID = %s) AND useDate = %s AND facility = %s"
            sqlVar = (rfid, today, facility)

            #Run SQL Query
            cur.execute(sql, sqlVar)
            result = cur.fetchall()

            cur.close()
            conn.close()

            if not result:
                message = "False"
                return message, 200

            start = datetime.datetime.strptime(result[-1][1], '%H:%M:%S').time()
            end = datetime.datetime.strptime(result[-1][2], '%H:%M:%S').time()

            endVar = result[-1][2]
            nowVar = datetime.datetime.now().strftime("%H:%M:%S")

            #resFacility = result[][0]
            resource = result[-1][0]
            timeVar = timeLeft(nowVar, endVar)

            print (result)
            if (start <= now) and (now <= end):
                message = "True," + str(resource) + "," + str(timeVar)
            else:
                message = "False"
        except mariadb.Error as e:
            print(f"Error: {e}")
    return message, 200

#Run Server
if __name__ == "__main__":
    app.run(debug=True)

