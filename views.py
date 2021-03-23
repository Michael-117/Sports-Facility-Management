"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from app import app
from app import db
from app.models import User
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


@app.route('/booking/')
def booking():


    return render_template("booking.html",booking=booking)

    



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


if __name__ == '__main__':
    app.secret_key=os.urandom(12)
    app.run(debug=True, host="0.0.0.0", port="8080")
