"""
                    Table of Contents
------------------------------------------------------
------------------------------------------------------
Imports                     =           Line 42
Global Variables            =           Line 54

                        Classes                   
---------------------------------------------------
User class                  =           Line 94
---------------------------------------------------
                    Helper Functions
---------------------------------------------------
allowed_file                =           Line 107
timeLeft                    =           Line 112
getTimes                    =           Line 122
generateSessions            =           Line 132
updateBookingStatuses       =           Line 180
---------------------------------------------------
                     App Functions
---------------------------------------------------
app.before_request          =           Line 200
Login                       =           Line 215
Logout                      =           Line 263
Header                      =           Line 269
Base                        =           Line 274
Home                        =           Line 279
Footer                      =           Line 284
Profile                     =           Line 291
Booking                     =           Line 369
View Booking                =           Line 575
Facility Management         =           Line 707
Resource Management         =           Line 829
User Management             =           Line 917
Card Management             =           Line 1074
System Logs                 =           Line 1210
Verify Booking              =           Line 1297
"""

"""Imports"""

import datetime
import hashlib
import math
import mysql.connector as mariadb
import os
from dateutil.relativedelta import *
from flask import Flask, flash, g, redirect, render_template, request, session
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

"""Global Variables"""

now = datetime.datetime.now()
lastMonth = now - relativedelta(months=1)
lastWeek = now - relativedelta(weeks=1)
twoWeeksAgo = now - relativedelta(weeks=2)
dateTomorrow = now + relativedelta(days=1)
nextWeek = now + relativedelta(weeks=1)
nextMonth = now + relativedelta(months=1)
nowString = now.strftime("%Y-%m-%d %H:%M:%S")
lastMonthString = lastMonth.strftime("%Y-%m-%d")
twoWeeksAgoString = twoWeeksAgo.strftime("%Y-%m-%d")
lastWeekString = lastWeek.strftime("%Y-%m-%d")
dateToday = now.strftime("%Y-%m-%d")
nextWeekString = nextWeek.strftime("%Y-%m-%d")
nextMonthString = nextMonth.strftime("%Y-%m-%d")
timeNow = now.strftime("%H:%M:%S")
timeNow2 = now.strftime("%H:%M")
dateString1 = dateToday + " 00:00:00"
dateString2 = dateToday + " 23:59:59"
weekString = lastWeekString + " 00:00:00"
monthString = lastMonthString + " 00:00:00"
users = []

UPLOAD_FOLDER = '/var/www/html/FlaskApp/SFMS/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sfacility.pd@gmail.com'
app.config['MAIL_PASSWORD'] = 'new_Password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.secret_key = "12345"
mail = Mail(app)


"""Classes"""

#User Class for global variable
class User:
    def __init__(self, id, username, firstname, userType):
        self.id = id
        self.username = username
        self.firstname = firstname
        self.userType = userType

    def __repr__(self):
        return f'<User: {self.username}>'

"""Helper Functions"""

#Function to check for file allowances
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Function to calculate time remaining for a booking based off current time and booking end time
def timeLeft(nowTime: str, endTime: str):
    nowVals = nowTime.split(":")
    endVals = endTime.split(":")
    hrsDiff = int(endVals[0]) - int(nowVals[0])
    minsDiff = int(endVals[1]) - int(nowVals[1])
    secDiff = int(endVals[2]) - int(nowVals[2])
    secsLeft = (hrsDiff*3600) + (minsDiff*60) + (secDiff)
    return secsLeft

#Function to determine start and end time for a booking
def getTimes(session: str):
    startEnd = []
    session = session.strip().split("-")
    start = session[0].rstrip() + ":" + "00"
    end = session[1] + ":" + "00"
    startEnd.append(start)
    startEnd.append(end)
    return startEnd

#Function to generate the sessions for a resource
def generateSessions(sessionLength: str, gracePeriod: str, dateToday: str):

    sessionLength = int(sessionLength)
    todayVar = dateToday.split("-")
    baseTime = datetime.datetime(int(todayVar[0]),int(todayVar[1]),int(todayVar[2]),0,0,0)
    sessions = []
    times = []
    startTimes = []
    endTimes = []
    sTimes = []
    dates = []
    sessionTimes = []

    sessionQuantity = math.floor((24 * 60) / (sessionLength + int(gracePeriod)))
    times.append(baseTime.strftime("%H:%M"))

    for i in range(0,3):
        timeVar = baseTime + relativedelta(days=i)
        dates.append(timeVar.strftime("%Y-%m-%d"))

    for i in range(1, sessionQuantity+1):
        gen = (i*sessionLength)
        sessions.append(gen)

    for i in sessions:
        baseTime = baseTime + relativedelta(minutes = int(gracePeriod))
        timeVar = baseTime + relativedelta(minutes=i)
        times.append(timeVar.strftime("%H:%M"))

    startTimes = times[::2]
    endTimes = times[1::2]

    endTimes.append(baseTime.strftime("%H:%M"))

    for i in range(0,len(startTimes)-1):
        sessionTimes.append(startTimes[i] + " - " + endTimes[i])
        sTimes.append(startTimes[i])

        if i == len(startTimes):
            sessionTimes.append(endTimes[i] + " - " + baseTime.strftime("%H:%M"))
            sTimes.append(endTimes[i])
        else:
            sessionTimes.append(endTimes[i] + " - " + startTimes[i+1])
            sTimes.append(endTimes[i])

    return sessionTimes, sTimes, dates

#Update Booking statuses based on current time    
def updateBookingStatuses():
    try:
        now = datetime.datetime.now()
        tn2 = now.strftime("%H:%M:%S")

        #Connect to DB
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()
        sql = "UPDATE Booking SET status = 'Ended' WHERE useDate <= CONVERT(%s, DATE) AND status = 'Upcoming' AND useEnd <= CONVERT(%s, TIME)"
        sqlVar = (dateToday, tn2)
        cur.execute(sql, sqlVar)
        conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Error: {e}")

"""Basic App Functions"""

#Check for session before each request, create global variable with logged in user for use with other pages on domain
@app.before_request
def before_request():
    g.user = None
    if 'user_ID' in session:
        for x in users:
            if x.id == session['user_ID']:
                g.user = x

    #Check if there is a user stored in global variable i.e. Someone is logged in
    if not g.user:
        flash("You must log in for access")
        return redirect('/SFMS/login')

#Login
@app.route('/login', methods=['post', 'get'])
def login():

	#Remove session
    session.pop('user_ID', None)

    if(request.method=='POST'):

	    #Get username and password from POST request
        username = request.form.get('username')
        passwordEntry = request.form.get('password')

	    #Hash password with SHA256 Algorithm
        entryPasswordHash = hashlib.sha256(passwordEntry.encode('utf-8')).hexdigest()

        try:
	        #Connect to DB
            conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
            cur = conn.cursor()

	        #Search for user by username
            sql = "SELECT sesame, userID, firstName, userType FROM SFMSUser WHERE username = %s"
            sqlVar = (username, )
            cur.execute(sql, sqlVar)
            result = cur.fetchall()

            #If user invalid, return to login screen
            if not result:
                flash("User not found")
                return render_template('login.html')

	        #Test for password match
            if result[0][0] == entryPasswordHash:

    	        #Create Session
                session['user_ID'] = result[0][1]
                users.append(User(result[0][1], username, result[0][2], result[0][3]))
                cur.close()
                conn.close()
                flash('You have successfully logged in')
                #Redirect to profile page
                return redirect('/SFMS/profile')
        except mariadb.Error as e:
            print(f"Error: {e}")

    return render_template('login.html')

#Logout
@app.route('/logout')
def logout():
    flash('You were logged out')
    return redirect('/SFMS/login')

#Webpage Header
@app.route('/header')
def header():
    return render_template('header.html')

#Base Webpage
@app.route('/base')
def base():
    return render_template('base.html')

#App Home Page
@app.route('/')
def home():
    return render_template('home.html')

#Webpage Footer
@app.route('/footer')
def footer():
    return render_template('footer.html')

"""App Functions"""

#Profile Page
@app.route('/profile', methods=['post','get'])
def profile():
    
    #Get user image

    try:
        #Connect to DB
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()
        sql = "SELECT image FROM SFMSUser WHERE userID = %s"
        sqlVar = (g.user.id,)
        cur.execute(sql,sqlVar)
        result = cur.fetchone()
        imageURL = result[0]
        cur.close()
        conn.close()
        
    except mariadb.Error as e:
                print(f"Error: {e}")

    if (request.method == 'POST'):

        #Change user password

        if 'change' in request.form:
            password = request.form.get('p2')
            hashedPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "UPDATE SFMSUser SET sesame = %s WHERE userID = %s"
                sqlVar = (hashedPassword, g.user.id)
                cur.execute(sql,sqlVar)
                conn.commit()
                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('Password changed successfully')
            return redirect('/SFMS/profile')
        
        #Upload new user image

        if 'upload' in request.form:
            if 'file' not in request.files:
                flash('No Picture Uploaded')
                return redirect('/SFMS/profile')

            image = request.files['file']

            if image and allowed_file(image.filename):
                upimageURL = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], upimageURL))
                imageRef = "/SFMS/static/uploads/" + upimageURL
            else:
                imageRef = "/SFMS/static/uploads/" + "noimage.png"

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "UPDATE SFMSUser SET image = %s WHERE userid = %s"
                sqlVar = (imageRef, g.user.id)
                cur.execute(sql,sqlVar)
                conn.commit()           
                cur.close()
                conn.close()
            except mariadb.Error as e:
                    print(f"Error: {e}")

            flash('Profile picture changed successfully')
            return redirect('/SFMS/profile')

    return render_template('profile.html', image = imageURL)

#Create Booking
@app.route('/booking', methods=['post', 'get'])
def booking():

    facilitynames = []
    facilityids = []
    usernames = []
    userids = []
    resources = []
    sessions1 = []
    sessions2 = []
    sessions1ids = []
    sessions2ids = []
    
    #Retrieve System Users and Facilities
    try:
        #Connect to DB
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()
        sql = "SELECT facilityName, facilityID FROM Facility"
        cur.execute(sql,)
        result = cur.fetchall()

        for i in range(0,len(result)):
            facilitynames.append(result[i][0])
            facilityids.append(result[i][1])
        
        sql = "SELECT username, userID FROM SFMSUser"
        cur.execute(sql,)
        result = cur.fetchall()

        for i in range(0,len(result)):
            usernames.append(result[i][0])
            userids.append(result[i][1])

        cur.close()
        conn.close()

    except mariadb.Error as e:
                print(f"Error: {e}")

    if (request.method == 'POST'):
        now = datetime.datetime.now()
        tn2 = now.strftime("%H:%M:%S")


        # Search for available resources and booking session slots by facility

        if "search" in request.form:
            facilityID = request.form.get('facilityID')
            date = request.form.get('date')
            execuserID = request.form.get('user')
            tablename = ""
            tablenameRes = ""
        
            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "SELECT facilityName FROM Facility WHERE facilityID = %s"
                sqlVar = (facilityID,)
                cur.execute(sql, sqlVar)
                result = cur.fetchone()
                facilityName = result[0]
                tableVar = facilityName.split(" ")
                tablename = tableVar[0][0] + tableVar[1][0] + "R"
                sql = "SELECT resourceNumber FROM Resources WHERE facilityID = %s AND status = %s"
                sqlVar = (facilityID,"Available")
                cur.execute(sql, sqlVar)
                result = cur.fetchall()

                for i in range(0,len(result)):
                    tablenameRes = tablename + str(result[i][0])

                    #Retrieve free booking session slots for today with time later than now
                    if date == dateToday:
                        sql = "SELECT sessionRange, slotID FROM {} WHERE date = %s AND startTime >= CONVERT(%s, TIME) AND status = 'free' ".format(tablenameRes)
                        sqlVar = (date, tn2)
                        cur.execute(sql, sqlVar)
                        result2 = cur.fetchall()

                    #Retrieve free booking session slots for selected date
                    else:  
                        sql = "SELECT sessionRange, slotID FROM {} WHERE date = %s AND status = 'free' ".format(tablenameRes)
                        sqlVar = (date, tn2)
                        cur.execute(sql, sqlVar)
                        result2 = cur.fetchall()

                    if result[i][0] == 1:
                        for j in range(0,len(result2)):
                            sessions1.append(result2[j][0])
                            sessions1ids.append(result2[j][1])
                    if result[i][0] == 2:
                        for j in range(0,len(result2)):
                            sessions2.append(result2[j][0])
                            sessions2ids.append(result2[j][1])

                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")
            
            return render_template('booking2.html', sessions1 = sessions1, sessions2 = sessions2, facilityName = facilityName, facilityID = facilityID, date = date, sessions1ids = sessions1ids, sessions2ids = sessions2ids, tbl = tablename, user = execuserID)

        #Booking Resource 1
        if "book1" in request.form:
            date = request.form.get('date')
            session = request.form.get('r1choice')
            sessionid = request.form.get('r1choiceID')
            facilityID = request.form.get('facilityID')
            resourceNum = request.form.get('resourceNum')
            tablename = request.form.get('tbl')
            execuserID = request.form.get('user')
            sessVals = session.split("|")
            session = sessVals[0]
            sessionID = sessVals[1]
            getTimes(session)
            times = getTimes(session)
            start = times[0]
            end = times[1]

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Admin booking for another user
                if g.user.userType == 'admin':
                    sql = "INSERT INTO `Booking`(`resourceNumber`, `facilityID`, `useStart`, `useEnd`, `useDate`, `userID`) VALUES (%s,%s,%s,%s,%s,%s)"
                    sqlVar = (resourceNum, facilityID, start, end, date, execuserID)
                
                #Normal Booking
                else:
                    sql = "INSERT INTO `Booking`(`resourceNumber`, `facilityID`, `useStart`, `useEnd`, `useDate`, `userID`) VALUES (%s,%s,%s,%s,%s,%s)"
                    sqlVar = (resourceNum, facilityID, start, end, date, g.user.id)

                cur.execute(sql, sqlVar)
                conn.commit()
                sql = "SELECT MAX(bookingID) FROM Booking"
                cur.execute(sql,)
                result = cur.fetchone()
                bookingID = result[0]
                sql = "UPDATE {} SET status = 'booked', bookingID = %s WHERE slotID = %s".format(tablename)
                sqlVar = (bookingID, sessionID)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('Booking created successfully for Resource 1')
            return redirect('/SFMS/booking')

        #Booking Resource 2
        if "book2" in request.form:
            date = request.form.get('date')
            session = request.form.get('r2choice')
            sessionid = request.form.get('r2choiceID')
            facilityID = request.form.get('facilityID')
            resourceNum = request.form.get('resourceNum')
            tablename = request.form.get('tbl')
            sessVals = session.split("|")
            session = sessVals[0]
            sessionID = sessVals[1]
            getTimes(session)
            times = getTimes(session)
            start = times[0]
            end = times[1]

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Admin booking for another user
                if g.user.userType == 'admin':
                    sql = "INSERT INTO `Booking`(`resourceNumber`, `facilityID`, `useStart`, `useEnd`, `useDate`, `userID`) VALUES (%s,%s,%s,%s,%s,%s)"
                    sqlVar = (resourceNum, facilityID, start, end, date, execuserID)
                
                #Normal Booking
                else:
                    sql = "INSERT INTO `Booking`(`resourceNumber`, `facilityID`, `useStart`, `useEnd`, `useDate`, `userID`) VALUES (%s,%s,%s,%s,%s,%s)"
                    sqlVar = (resourceNum, facilityID, start, end, date, g.user.id)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                sql = "SELECT MAX(bookingID) FROM Booking"
                cur.execute(sql,)
                result = cur.fetchone()
                bookingID = result[0]
                sql = "UPDATE {} SET status = 'booked', bookingID = %s WHERE slotID = %s".format(tablename)
                sqlVar = (bookingID, sessionID)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('Booking created successfully for Resource 2')
            return redirect('/SFMS/booking')
        
    return render_template('booking1.html', facilityName = facilitynames, facilityids = facilityids, today = dateToday, endRange = nextMonthString, usernames = usernames, userids = userids)

#View Bookings
@app.route('/viewbooking', methods = ['post', 'get'])
def viewbooking():

    bookingids = []
    bookingdatetime = []
    resourceNums = []
    resourcenames = []
    facilityids = []
    facilitynames = []
    starttimes = []
    endtimes = []
    usedate = []
    userids = []
    usernames = []
    status = []
    tableNames = []
    
    updateBookingStatuses()

    #Retrieve bookings based on member type 
    if(request.method == 'POST'):
        if 'viewBooking' in request.form:
            viewRange = request.form.get('range')

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                if (g.user.userType == "admin" and viewRange == 'today'):
                    sql = "SELECT * FROM Booking WHERE useDate = %s"
                    sqlVar = (dateToday,)

                if (g.user.userType == "admin" and viewRange == 'week'):
                    sql = "SELECT * FROM Booking WHERE useDate BETWEEN %s AND %s"
                    sqlVar = (dateToday,nextWeekString)

                if (g.user.userType == "admin" and viewRange == 'month'):
                    sql = "SELECT * FROM Booking WHERE useDate BETWEEN %s AND %s"
                    sqlVar = (dateToday,nextMonthString)
                
                if (g.user.userType == "member" and viewRange == 'today'):
                    sql = "SELECT * FROM Booking WHERE (useDate = %s) AND userID = %s"
                    sqlVar = (dateToday, g.user.id)

                if (g.user.userType == "member" and viewRange == 'week'):
                    sql = "SELECT * FROM Booking WHERE (useDate BETWEEN %s AND %s) AND (userID = %s)"
                    sqlVar = (dateToday,nextWeekString, g.user.id)

                if (g.user.userType == "member" and viewRange == 'month'):
                    sql = "SELECT * FROM Booking WHERE (useDate BETWEEN %s AND %s) AND (userID = %s)"
                    sqlVar = (dateToday,nextMonthString, g.user.id)

                cur.execute(sql,sqlVar)
                result = cur.fetchall()

                for i in range(0,len(result)):
                    bookingids.append(result[i][0])
                    bookingdatetime.append(result[i][1])
                    resourceNums.append(result[i][2])
                    facilityids.append(result[i][3])
                    starttimes.append(result[i][4])
                    endtimes.append(result[i][5])
                    usedate.append(result[i][6])
                    userids.append(result[i][7])
                    status.append(result[i][8])

                for i in range(0, len(userids)):
                    sql = "SELECT username from SFMSUser WHERE userID = %s"
                    sqlVar = (userids[i],)
                    cur.execute(sql,sqlVar)
                    result = cur.fetchone()
                    usernames.append(result[0])

                for i in range(0, len(resourceNums)):
                    sql = "SELECT resourceName from Resources WHERE facilityID = %s AND resourceNumber = %s"
                    sqlVar = (facilityids[i], resourceNums[i],)
                    print(sql, sqlVar)
                    cur.execute(sql,sqlVar)
                    result = cur.fetchone()
                    resourcenames.append(result[0])

                for i in range(0, len(facilityids)):
                    sql = "SELECT facilityName from Facility WHERE facilityID = %s"
                    sqlVar = (facilityids[i],)
                    cur.execute(sql,sqlVar)
                    result = cur.fetchone()
                    facilitynames.append(result[0])

                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

        #Cancel by ID
        if 'cancel' in request.form:
            bookingID = request.form.get('bookingid')

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "SELECT facilityID, resourceNumber FROM Booking WHERE bookingID = %s"
                sqlVar = (bookingID,)
                cur.execute(sql, sqlVar)
                result = cur.fetchone()
                resourceNum = result[1]
                sql = "SELECT facilityName FROM Facility WHERE facilityID = %s"
                sqlVar = (result[0],)
                cur.execute(sql, sqlVar)
                facilityName = cur.fetchone()
                tableVar = facilityName[0].split(" ")
                tablename = tableVar[0][0] + tableVar[1][0] + "R" + str(resourceNum)
                sql = "UPDATE Booking SET status = 'Cancelled' WHERE bookingID = %s"
                sqlVar = (bookingID,)
                cur.execute(sql, sqlVar)
                conn.commit()
                sql = "UPDATE {} SET status = 'free', bookingID = NULL WHERE bookingID = %s".format(tablename)
                sqlVar = (bookingID,)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('Booking cancelled successfully')
            return redirect('/SFMS/viewbooking')

    return render_template('manageBooking.html', bookingids = bookingids, bookingdatetime = bookingdatetime, resourcenames = resourcenames, facilitynames = facilitynames, starttimes = starttimes, endtimes = endtimes, usedate = usedate, usernames = usernames, resourceNums = resourceNums, status = status)

#Facility Management
@app.route('/facilitymanagement', methods=['post','get'])
def newFacility():
    #Check for admin member type
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    facilities = []
    resourceName = []
    status = []

    #Retrieve facilities in system
    try:
        #Connect to DB
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()
        sql = "SELECT facilityName FROM Facility"
        cur.execute(sql,)
        result = cur.fetchall()
        cur.close()
        conn.close()

        for i in range(0,len(result)):
            facilities.append(result[i][0])

    except mariadb.Error as e:
        print(f"Error: {e}")

    if (request.method == 'POST'): 

        #Add new facility to system
        if 'addFacility' in request.form:
            facilityName = request.form.get('facilityName')
            resourceName.append(request.form.get('r1'))
            resourceName.append(request.form.get('r2'))
            status.append(request.form.get('status1'))
            status.append(request.form.get('status2'))
            sessionLength = request.form.get('session')
            gracePeriod = request.form.get('grace')
            sessionTimes, sTimes, dates = generateSessions(sessionLength,gracePeriod, dateToday)

            if (len(facilityName.split()) == 1):
                facilityName = facilityName.rstrip() + " Facility"

            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "INSERT INTO Facility (facilityName, sessionLength, gracePeriod) VALUES (%s, %s, %s)"
                sqlVar = (facilityName, sessionLength, gracePeriod)
                cur.execute(sql, sqlVar)
                conn.commit()
                sql = "SELECT MAX(facilityID) FROM Facility"
                cur.execute(sql,)
                result = cur.fetchone()
                facilityID = result[0]

                for i in range(0, len(resourceName)):
                    resourceNum = i+1
                    sql = "INSERT INTO Resources (resourceName, resourceNumber, facilityID, status) VALUES (%s, %s, %s, %s)"
                    sqlVar = (resourceName[i], resourceNum, facilityID, status[i])
                    cur.execute(sql, sqlVar)
                    conn.commit()
                    tableVar = facilityName.split(" ")
                    tablename = tableVar[0][0] + tableVar[1][0] + "R" + str(resourceNum)
                    sql = "DROP TABLE IF EXISTS {}".format(tablename)                    
                    cur.execute(sql,)
                    conn.commit()
                    sql = "CREATE TABLE {} (slotID int(11) AUTO_INCREMENT NOT NULL PRIMARY KEY, sessionRange varchar(255) NOT NULL, startTime time NOT NULL, bookingID int(11), status varchar(10) NOT NULL DEFAULT 'free', date date NOT NULL)".format(tablename)
                    cur.execute(sql, )
                    conn.commit()

                    for i in dates:
                        for j in sessionTimes:
                            sql = "INSERT INTO {} (sessionRange, startTime, date) VALUES (%s, %s, %s)".format(tablename)
                            sqlVar = (j, sTimes[sessionTimes.index(j)], i)
                            cur.execute(sql,sqlVar)
                            conn.commit()

                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('New facility, {} created'.format(facilityName))
            return redirect('/SFMS/facilitymanagement')

        #Remove facility from system
        if 'remove' in request.form:
            facilityName = request.form.get('facilityName')
            tableVar = facilityName.split(" ")
            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "DELETE FROM Resources WHERE facilityID = (SELECT facilityID from Facility WHERE facilityName = %s)"
                sqlVar = (facilityName,)
                cur.execute(sql, sqlVar)
                conn.commit()
                sql = "DELETE FROM Booking WHERE facilityID = (SELECT facilityID from Facility WHERE facilityName = %s)"
                sqlVar = (facilityName,)
                cur.execute(sql, sqlVar)
                conn.commit()

                for i in range(1,3):
                    tablename = tableVar[0][0] + tableVar[1][0] + "R" + str(i)                
                    sql = "DROP TABLE {}".format(tablename)
                    cur.execute(sql,)
                    conn.commit()

                sql = "DELETE FROM Facility WHERE facilityName = %s"
                sqlVar = (facilityName,)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")
            flash('{} removed'.format(facilityName))
            return redirect('/SFMS/facilitymanagement')

    return render_template("manageFacility.html", facilities = facilities)

#Resource Management
@app.route('/resourcemanagement', methods=['post','get'])
def manageResources():
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    facilityName = ""
    resources = ""
    resourceNum = ""
    status = ""


    if (request.method == 'POST'):

        #Manage resources based on chosen facility
        if "manage" in request.form:
            facilityName = request.form.get('facilityName')
            resources = []
            resourceNum = []
            status = []

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "SELECT resourceName, resourceNumber, status FROM Resources WHERE facilityID = (SELECT facilityID FROM Facility WHERE facilityName = %s)"
                sqlVar = (facilityName,)
                cur.execute(sql, sqlVar)
                result = cur.fetchall()
                cur.close()
                conn.close()

                for i in range(0,len(result)):
                    resources.append(result[i][0])
                    resourceNum.append(result[i][1])
                    status.append(result[i][2])

            except mariadb.Error as e:
                print(f"Error: {e}")
        
        #Update resource status
        if "updateStatus" in request.form:
            facilityName = request.form.get('facilityName')
            resourceNum = request.form.get('resourceNum')
            status = request.form.get('status')

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "UPDATE Resources SET status = %s WHERE (facilityID = (SELECT facilityID FROM Facility WHERE facilityName = %s)) AND (resourceNumber = %s)"
                sqlVar = (status, facilityName, resourceNum)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
                
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('{}, Resource {} status updated'.format(facilityName, resourceNum))
            return redirect('/SFMS/facilitymanagement')

        #Rename a resource
        if "rename" in request.form:
            facilityName = request.form.get('facilityName')
            resourceNum = request.form.get('resourceNum')
            newresourceName = request.form.get('newresourceName')

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "UPDATE Resources SET resourceName = %s WHERE (facilityID = (SELECT facilityID FROM Facility WHERE facilityName = %s)) AND (resourceNumber = %s)"
                sqlVar = (newresourceName, facilityName, resourceNum)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
                
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('{}, Resource {} renamed to {}'.format(facilityName, resourceNum, newresourceName))
            return redirect('/SFMS/facilitymanagement')

    return render_template('manageResource.html', facilityName = facilityName, resources = resources, resourceNum = resourceNum, status = status)

#User Management
@app.route('/usermanagement', methods=['post','get'])
def newUser():
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    fname = []
    lname = []
    usernames = []
    fname2 = []
    lname2 = []
    usernames2 = []

    try:
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()
        sql = "SELECT firstName, lastName, username FROM SFMSUser WHERE userType != 'SYSTEM' AND status = 'active' AND userID != '2'"
        cur.execute(sql,)
        result = cur.fetchall()

        for i in range(0,len(result)):
            fname.append(result[i][0])
            lname.append(result[i][1])
            usernames.append(result[i][2])

        sql = "SELECT firstName, lastName, username FROM SFMSUser WHERE userType != 'SYSTEM' AND status = 'inactive' AND userID != '2'"
        cur.execute(sql,)
        result = cur.fetchall()
        cur.close()
        conn.close()

        for i in range(0,len(result)):
            fname2.append(result[i][0])
            lname2.append(result[i][1])
            usernames2.append(result[i][2])

    except mariadb.Error as e:
        print(f"Error: {e}")
    
    #Retrieve POST Request Data
    if (request.method == 'POST'): 
        
        #Add a user to the system
        if "adduser" in request.form:

            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            username = request.form.get('username')
            usertype = request.form.get('usertype')
            useraddress = request.form.get('useraddress')
            useremail = request.form.get('useremail')
            telephone = request.form.get('telephone')
            password = firstname.lower() + lastname.lower() + "123"
            hashedPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()

            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "INSERT INTO SFMSUser (firstName, lastName, username, userType, userAddress, email, telephone, sesame, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                sqlVar = (firstname, lastname, username, usertype, useraddress, useremail, telephone, hashedPassword, "active")
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")
            
            mailcontent = Message('Welcome to SFMS', sender = 'sfmsadmin@gmail.com', recipients = [useremail])
            mailcontent.body = "Hello {},\nYour username is {}.\nYour password is {}.\nPlease remember to log in and change this default password as soon as possible.\nYou can log in to the system at the link below:\nhttps://mpearnet.ngrok.io/SFMS/login".format(firstname,username,password)
            mail.send(mailcontent)

            flash('New user {} {} created'.format(firstname, lastname))
            return redirect('/SFMS/usermanagement')

        #Deaactuvate a user
        if "deactivate" in request.form:
            username = request.form.get('username')
            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "SELECT firstName, lastName FROM SFMSUser WHERE username = %s"
                sqlVar = (username,)
                cur.execute(sql, sqlVar)
                result = cur.fetchone()
                firstname = result[0]
                lastname = result[1]
                sql = "UPDATE SFMSUser SET status = %s WHERE username = %s"
                sqlVar = ("inactive",username)
                cur.execute(sql, sqlVar)
                conn.commit()
                sql = "UPDATE Cards SET userID = 1 WHERE userID = (SELECT userID FROM SFMSUser WHERE username = %s)"
                sqlVar = (username,)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('User {} {} deactivated'.format(firstname, lastname))
            return redirect('/SFMS/usermanagement')

        #Remove a user from system
        if "remove" in request.form:
            username = request.form.get('username')
            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "SELECT firstName, lastName FROM SFMSUser WHERE username = %s"
                sqlVar = (username,)
                cur.execute(sql, sqlVar)
                result = cur.fetchone()
                firstname = result[0]
                lastname = result[1]
                sql = "DELETE FROM SFMSUser WHERE username = %s"
                sqlVar = (username,)
                cur.execute(sql, sqlVar)
                conn.commit()
                sql = "UPDATE Cards SET userID = 1 WHERE userID = (SELECT userID FROM SFMSUser WHERE username = %s)"
                sqlVar = (username,)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('User {} {} removed'.format(firstname, lastname))
            return redirect('/SFMS/usermanagement')

        #Activate a user
        if "activate" in request.form:
            username = request.form.get('username')
            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "SELECT firstName, lastName FROM SFMSUser WHERE username = %s"
                sqlVar = (username,)
                cur.execute(sql, sqlVar)
                result = cur.fetchone()
                firstname = result[0]
                lastname = result[1]
                sql = "UPDATE SFMSUser SET status = %s WHERE username = %s"
                sqlVar = ("active",username)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('User {} {} activated'.format(firstname, lastname))
            return redirect('/SFMS/usermanagement')

    return render_template("manageUser.html", firstname = fname, lastname = lname, username = usernames, firstname2 = fname2, lastname2 = lname2, username2 = usernames2)

#Assign RFID Card to Member
@app.route('/cardmanagement', methods = ['post', 'get'])
def assign():
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    users = []
    usernames = []
    userids = []
    newcards = []
    usedcards = []

    try:
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()
        sql = "SELECT username FROM SFMSUser"
        cur.execute(sql,)
        result = cur.fetchall()
        for i in range(0,len(result)):
            users.append(result[i][0])
        sql = "SELECT cardID FROM Cards WHERE userID = 1"
        cur.execute(sql,)
        result = cur.fetchall()
        for i in range(0,len(result)):
            newcards.append(result[i][0])
        sql = "SELECT cardID, userID FROM Cards WHERE userID != 1"
        cur.execute(sql,)
        result = cur.fetchall()
        for i in range(0,len(result)):
            usedcards.append(result[i][0])
            userids.append(result[i][1])

        for i in userids:
            sql = "SELECT username FROM SFMSUser WHERE userID = %s"
            sqlVar = (i,)
            cur.execute(sql,sqlVar)
            result = cur.fetchone()
            usernames.append(result[0])

        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Error: {e}")

    if(request.method =='POST'):

        #Assign a new card to a user
        if 'assignNew' in request.form:
            username = request.form.get('username')
            chosenRFID = request.form.get('newcards')
            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "UPDATE Cards SET userID = (SELECT userID FROM SFMSUser WHERE username = %s) WHERE cardID = %s"
                sqlVar = (username, chosenRFID)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('Card {} assigned to {}'.format(chosenRFID, username))
            return redirect('/SFMS/cardmanagement')

        #Reassign a card from one user to another
        if 'reassign' in request.form:
            username = request.form.get('username')
            chosenRFID = request.form.get('usedcards')
            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "SELECT cardID FROM Cards WHERE userID = (SELECT userID FROM SFMSUser WHERE username = %s)"
                sqlVar = (username,)
                cur.execute(sql, sqlVar)
                result = cur.fetchall()

                if result:
                    sql = "UPDATE Cards SET userID = '1' WHERE cardID = %s"
                    sqlVar = (result[0][0],)
                    cur.execute(sql, sqlVar)
                    conn.commit()

                sql = "UPDATE Cards SET userID = (SELECT userID FROM SFMSUser WHERE username = %s) WHERE cardID = %s"
                sqlVar = (username, chosenRFID)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('Card {} successfully reassigned to {}'.format(chosenRFID, username))
            return redirect('/SFMS/cardmanagement')

        #Add new card to system
        if 'addNew' in request.form:
            rfid = request.form.get('addcard')
            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "INSERT INTO Cards (userID, cardID) VALUES (%s, %s)"
                sqlVar = ("1",rfid)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")
            
            flash('New Card {} successfully added'.format(rfid))
            return redirect('/SFMS/cardmanagement')

        #Delete a card from a system
        if 'delete' in request.form:
            rfid = request.form.get('deleteCard')
            try:
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()
                sql = "DELETE FROM Cards WHERE cardID = %s"
                sqlVar = (rfid,)
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
            except mariadb.Error as e:
                print(f"Error: {e}")

            flash('Card {} removed successfully'.format(rfid))
            return redirect('/SFMS/cardmanagement')

    return render_template("manageCard.html", users = users, newcards = newcards, usedcards = usedcards, usernames = usernames)

#System Logs
@app.route('/systemlogs', methods=['post','get'])
def systemlogs():
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    firstName = []
    lastName = []
    facilityID = []
    ufacilityID = []
    facilityName = []
    ufacilityName = []
    readingTime = []
    ureadingTime = []
    userids = []
    rfid = []
    urfid = []

    if(request.method == 'POST'):
        date1 = request.form.get('date1') + " 00:00:00"
        now2 = datetime.datetime.now()
        nowString2 = now2.strftime("%Y-%m-%d %H:%M:%S")

        #Retrieve logs of known and unknown card access attempts between chosen date and now
        try:
            conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
            cur = conn.cursor()
            sql = "SELECT facilityID, rfid, reading_time FROM KnownCards WHERE reading_time BETWEEN %s AND %s"
            sqlVar = (date1, nowString2)
            cur.execute(sql,sqlVar)
            result = cur.fetchall()

            for i in range(0,len(result)):
                facilityID.append(result[i][0])
                rfid.append(result[i][1])
                readingTime.append(result[i][2])

            for i in range(0,len(rfid)):
                sql = "SELECT userID FROM Cards WHERE cardID = %s"
                sqlVar = (rfid[i],)
                cur.execute(sql,sqlVar)
                result = cur.fetchone()
                userids.append(result[0])

            for i in range(0,len(userids)):
                sql = "SELECT firstName, lastName FROM SFMSUser WHERE userID = %s"
                sqlVar = (userids[i],)
                cur.execute(sql,sqlVar)
                result = cur.fetchall()
                for j in range(0,len(result)):
                    firstName.append(result[j][0])
                    lastName.append(result[j][1])

            for i in range(0, len(facilityID)):
                sql = "SELECT facilityName FROM Facility WHERE facilityID = %s"
                sqlVar = (facilityID[i],)
                cur.execute(sql,sqlVar)
                result = cur.fetchall()
                for j in range(0,len(result)):
                    facilityName.append(result[j][0])

            sql = "SELECT facilityID, rfid, reading_time FROM UnknownCards WHERE reading_time BETWEEN %s AND %s"
            sqlVar = (date1, nowString2)
            cur.execute(sql,sqlVar)
            result = cur.fetchall()

            for i in range(0,len(result)):
                ufacilityID.append(result[i][0])
                urfid.append(result[i][1])
                ureadingTime.append(result[i][2])

            for i in range(0, len(ufacilityID)):

                sql = "SELECT facilityName FROM Facility WHERE facilityID = %s"
                sqlVar = (ufacilityID[i],)
                cur.execute(sql,sqlVar)
                result = cur.fetchall()
                for j in range(0,len(result)):
                    ufacilityName.append(result[j][0])

            cur.close()
            conn.close()
        except mariadb.Error as e:
            print(f"Error: {e}")

    return render_template('systemLog.html', firstName = firstName, lastName = lastName , facilityName = facilityName, ufacilityName = ufacilityName, readingTime = readingTime, ureadingTime = ureadingTime, today=dateToday, twoWeeksAgo = twoWeeksAgoString, lastMonth = lastMonthString, urfid = urfid)

#Verify Booking
@app.route('/verify', methods=['post', 'get'])
def verifyBooking():
    updateBookingStatuses()
    message = ""
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.today().time()

    if (request.method == 'POST'):
        name = request.form.get('sensor')
        facility = request.form.get('facilityID')
        rfid = request.form.get('rfid')

        #MasterCard On
        if (rfid =="5A797D7F"):
            message = "1,3,I"
            return message, 200

        #MasterCard Off
        if (rfid =="9C52BE"):
            message = "0,3,I"
            return message, 200

        try:
	        #Connect to DB
            conn = mariadb.connect(user="esp32", password="esp_boss5", host="localhost", database="SFM")
            cur = conn.cursor()
            sql = "SELECT * FROM Cards WHERE cardID = %s"
            sqlVar = (rfid,)
            cur.execute(sql, sqlVar)
            result = cur.fetchone()

            #Create SQL Query to log a facility access attempt with unknown card
            if result == None:
                sql = "INSERT INTO UnknownCards (sensor, facilityID, rfid) VALUES (%s, %s, %s)"
                sqlVar = (name, facility, rfid)
                cur.execute(sql, sqlVar)
                conn.commit()

            #Create SQL Query to log a facility access attempt with known card
            else:
                sql = "INSERT INTO KnownCards (sensor, facilityID, rfid) VALUES (%s, %s, %s)"
                sqlVar = (name, facility, rfid)
                cur.execute(sql, sqlVar)
                conn.commit()
                sql = "SELECT bookingID, resourceNumber, useStart, useEnd FROM Booking WHERE userID = (SELECT userID FROM Cards WHERE cardID = %s) AND useDate = %s AND facilityID = %s AND status = 'Upcoming'"
                sqlVar = (rfid, today, facility)
                cur.execute(sql, sqlVar)
                result = cur.fetchall()

                if not result:
                    message = "0,N"
                    return  message, 200
                
                bookingID = result[0][0]
                startVar = result[-1][2]
                endVar = result[-1][3]
                nowVar = datetime.datetime.now().strftime("%H:%M:%S")
                start = str(startVar)
                end = str(endVar)
                resource = result[-1][1]
                timeVar = timeLeft(nowVar, end)

                if (datetime.datetime.strptime(start, "%H:%M:%S").time() <= now) and (now <= datetime.datetime.strptime(end, "%H:%M:%S").time()):
                    sql = "UPDATE Booking SET status = 'Kept' WHERE bookingID = %s"
                    sqlVar = (bookingID,)
                    cur.execute(sql, sqlVar)
                    conn.commit()
                    cur.close()
                    conn.close()
                    message = "1," + str(resource) + "," + str(timeVar)
                else:
                    message = "0"

        except mariadb.Error as e:
            print(f"Error: {e}")
    return message, 200

#Run Server
if __name__ == "__main__":
    app.run(debug=True)

