from flask import Flask, render_template,request,session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app= Flask(__name__)
app.config['DEBUG'] = True
"""app.config['SQLALCHEMY_DATABASE_URI']='mysql://password@localhost/mydatabases'"""
app.config['SQLALCHEMY_DATABASE_URI']='mysqldb://password@localhost/mydatabases'
SQLALCHEMY_TRACK_MODIFICATIONS = True
db= SQLAlchemy(app)
app.secret_key = '1234'
"""
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # necessary to tell Flask-Login what the default route is for the login page
login_manager.login_message_category = "info"  # customize the flash message category
"""
from app import views