"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from flask import Flask
from flask import session,render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField,Form,TextField,TextAreaField, validators,SubmitField
from wtforms.validators import InputRequired
import os
from flask_sqlalchemy import SQLAlchemy
import schedule 
import time
import threading
from werkzeug.security import check_password_hash
os.chdir('..')
from forms import forms
from flask_login import current_user, login_user, logout_user, login_required
import mysql.connector as mariadb
import datetime

app= Flask(__name__)
app.config['DEBUG'] = True
"""app.config['SQLALCHEMY_DATABASE_URI']='mysql://password@localhost/mydatabases'"""
app.config['SQLALCHEMY_DATABASE_URI']='mysqldb://password@localhost/mydatabases'
SQLALCHEMY_TRACK_MODIFICATIONS = True
db= SQLAlchemy(app)
app.secret_key = '1234' 


###
# Routing for your application.
###
user={"username":"admin", "password": "password"}
@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/login', methods=['POST','GET'])
def login():
    error=None
    if(request.method=='POST'):
        username=request.form.get('username')
        password=request.form.get('password')
        if username==user['username'] and password==user['password']:
            session['user']=username
            return redirect('/')
        else:
            flash('wrong password!')
            return login()
    
    return render_template('login.html',error=error)
@app.route("/logout")
def logout():
    session['logged_in']=False









@app.route('/profile/')
def profile():
    """Render user's profile page."""
    return render_template('profile.html')


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



@app.route('/cancelbooking',methods=['GET','POST'])
@login_required
def cancelbooking():
    if not current_user.is_authenticated:
        flash('Please Log in to cancel booking')
        return redirect(url_for('login')) 
    
    form=CancelbookingForm()
    if form.validate_on_submit():
        meeting=Meeting.query.filter_by(id=form.ids.data).first()

        if meeting.date<=datetime.now():
            flash(f'Past booking cannot be canceled')
            return redirect(url_for('cancelbooking'))
        
        participants_user=Participants_user.query.filter_by(meeting=meeting.title).all()
        for part in participants_user:
            db.session.delete(part)
        participants_partner=Participants_partner.query.filter_by(meeting=meeting.title).all()
        for part in participants_partner:
            db.session.delete(part)
        
        costlog=CostLog.query.filter_by(title=meeting.title).first()
        db.session.delete(costlog)
        
        db.session.delete(meeting)
        db.session.commit()
        flash(f'Meeting {meeting.title} successfully deleted! ')
        return redirect(url_for('index'))
    return render_template('cancelbooking.html',title='Cancel Meeting',form=form)

@app.route('/roomavailable',methods=['GET','POST'])
def roomavailable():
    form=RoomavailableForm()
    if form.validate_on_submit():
        meetings=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).all()
        roomsOccupied=set()
        for meeting in meetings:
            if (form.startTime.data<meeting.endTime and (form.startTime.data+form.duration.data)>meeting.startTime): 
                roomsOccupied.add(Room.query.filter_by(id=meeting.roomId).first())
        rooms=Room.query.all()
        roomsavailable=[]
        for room in rooms:
            if room not in roomsOccupied:
                roomsavailable.append(room)
        return render_template('roomavailablelist.html',title='Room available',rooms=roomsavailable)
    return render_template('roomavailable.html',title='Room availability check',form=form)




###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

app.config.from_object(__name__)
if __name__ == '__main__':
    app.secret_key=os.urandom(12)
    app.run(debug=True, host="0.0.0.0", port="8080")
