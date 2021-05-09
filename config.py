from flask import Flask 
from flask import app
from flask import current_app
from flask import g

from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sfacility.pd@gmail.com'
app.config['MAIL_PASSWORD'] = 'new_Password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

#sql = "SELECT firstName, lastName FROM SFMSUser WHERE userID = (SELECT max(userID) FROM SFMSUser)"
fName = "Shawn"
lName = "McBean"
password = fName + lName + "123"


@app.route("/")
def index():
   msg = Message('Welcome to SFMS', sender = 'sfmsadmin@gmail.com', recipients = ['shawnmcbean96@gmail.com'])
   msg.body = "Hello, {}. \n \n Your password is {}. Please rememebr to log in and change this default password as soon as possible.".format(fName,password)
   mail.send(msg)
   return "Message Sent Successfully!"


if __name__ == '__main__':
   app.run(debug = True)