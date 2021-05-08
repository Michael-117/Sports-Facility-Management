"""
                    Table of Contents
------------------------------------------------------
------------------------------------------------------
Imports                     =           Lines
Global Variables            =           Lines

                        Classes                   
---------------------------------------------------
User class                  =           Lines 

                    Helper Functions
---------------------------------------------------
timeLeft function           =           Lines 
getTimes function           =           Lines 
generateSessions function   =           Lines 
---------------------------------------------------

                    App Functions
---------------------------------------------------
app.before_request          =           Lines 
Logout                      =           Lines 
Base                        =           Lines 
Header                      =           Lines 
Footer                      =           Lines 
ErrorPage                   =           Lines 
Login                       =           Lines 
Home                        =           Lines 
Profile                     =           Lines 
Booking                     =           Lines 
View Booking                =           Lines
Facility Management         =           Lines 
Resource Management         =           Lines
User Management             =           Lines  
Card Management             =           Lines 
System Logs                 =           Lines 
Verify Booking              =           Lines 
"""

"""Imports"""

import datetime
import hashlib
import math
import mysql.connector as mariadb
from dateutil.relativedelta import *
from flask import Flask, flash, g, redirect, render_template, request, session

"""Global Variables"""

now = datetime.datetime.now()
lastMonth = now - relativedelta(months=1)
lastWeek = now - relativedelta(weeks=1)
dateTomorrow = now + relativedelta(days=1)
nextWeek = now + relativedelta(weeks=1)
nextMonth = now + relativedelta(months=1)
lastMonthString = lastMonth.strftime("%Y-%m-%d")
lastWeekString = lastWeek.strftime("%Y-%m-%d")
dateToday = now.strftime("%Y-%m-%d")
#dateTomorrowString = dateTomorrow.strftime("%Y-%m-%d")
nextWeekString = nextWeek.strftime("%Y-%m-%d")
nextMonthString = nextMonth.strftime("%Y-%m-%d")
timeNow = now.strftime("%H:%M:%S")
timeNow2 = now.strftime("%H:%M")
users = []
app = Flask(__name__)
app.secret_key = "12345"


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

#Function to calculate time remaining for a booking based off current time, booking end time and a preset grace period
def timeLeft(nowTime: str, endTime: str, timeBuffer: str):
    nowVals = nowTime.split(":")
    endVals = endTime.split(":")
    hrsDiff = int(endVals[0]) - int(nowVals[0])
    minsDiff = int(endVals[1]) - int(nowVals[1]) + int(timeBuffer)
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
    gracePeriod = int(gracePeriod)
    todayVar = dateToday.split("-")
    baseTime = datetime.datetime(int(todayVar[0]),int(todayVar[1]),int(todayVar[2]),0,0,0)
    sessions = []
    times = []
    startTimes = []
    endTimes = []
    dates = []
    sessionTimes = []

    sessionQuantity = math.floor((24 * 60) / (sessionLength + gracePeriod))
    times.append(baseTime.strftime("%H:%M"))

    for i in range(0,31):
        timeVar = baseTime + relativedelta(days=i)
        dates.append(timeVar.strftime("%Y-%m-%d"))

    for i in range(1, sessionQuantity+1):
        gen = 0 + (i*(sessionLength + gracePeriod))
        sessions.append(gen)

    for i in sessions:
        timeVar = baseTime + relativedelta(minutes=i)
        times.append(timeVar.strftime("%H:%M"))

    startTimes = times[::2]
    endTimes = times[1::2]

    endTimes.append(baseTime.strftime("%H:%M"))

    for i in range(0,len(startTimes)-1):
        sessionTimes.append(startTimes[i] + " - " + endTimes[i])

        if i == len(startTimes):
            sessionTimes.append(endTimes[i] + " - " + baseTime.strftime("%H:%M"))
        else:
            sessionTimes.append(endTimes[i] + " - " + startTimes[i+1])

    return sessionTimes, dates
    

"""App Functions"""

#Check for session before each request, create global variable with logged in user for use with other pages on domain
@app.before_request
def before_request():
    g.user = None
    if 'user_ID' in session:
        for x in users:
            if x.id == session['user_ID']:
                g.user = x

@app.route('/logout')
def logout():
    return redirect('/SFMS/login')

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

#Login Page
@app.route('/login', methods=['post', 'get'])
def login():

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
            sql = "SELECT sesame, userID, firstName, userType FROM SFMSUser WHERE username = %s"
            sqlVar = (username, )

	    #Run SQL Query and retrieve records
            cur.execute(sql, sqlVar)
            result = cur.fetchall()

            if not result:
                return render_template('login.html')

	    #Test for password match
            if result[0][0] == entryPasswordHash:

    	        #Create Session
                session['user_ID'] = result[0][1]
                users.append(User(result[0][1], username, result[0][2], result[0][3]))
                cur.close()
                conn.close()

                #Redirect to profile page
                return redirect('/SFMS/profile')

        except mariadb.Error as e:
            print(f"Error: {e}")

    return render_template('login.html')

#Home Page
@app.route('/')
def home():
    return render_template('home.html')

#Profile Page
@app.route('/profile')
def profile():
    #Check if there is a user stored in global variable i.e. Someone is logged in
    if not g.user:
        return redirect('/SFMS/login')
    return render_template('profile.html')

#Create Booking
@app.route('/booking', methods=['post', 'get'])
def booking():
    if not g.user:
        return redirect('/SFMS/login')

    facilitynames = []
    facilityids = []
    resources = []
    sessions1 = []
    sessions2 = []
    sessions1ids = []
    sessions2ids = []
    
    try:
        #Connect to DB
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()

        #Create SQL Query
        sql = "SELECT facilityName, facilityID FROM Facility"

        #Run SQL Query
        cur.execute(sql,)
        result = cur.fetchall()

        for i in range(0,len(result)):
            facilitynames.append(result[i][0])
            facilityids.append(result[i][1])
        
        cur.close()
        conn.close()

    except mariadb.Error as e:
                print(f"Error: {e}")

    #Retrieve POST Request Data
    if (request.method == 'POST'):

        if "search" in request.form:
            facilityID = request.form.get('facilityID')
            date = request.form.get('date')
            tablename = ""
            tablenameRes = ""
        
            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Create SQL Query
                sql = "SELECT facilityName FROM Facility WHERE facilityID = %s"
                sqlVar = (facilityID,)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                result = cur.fetchone()
                facilityName = result[0]
                tableVar = facilityName.split(" ")
                tablename = tableVar[0][0] + tableVar[1][0] + "R"

                #Create SQL Query
                sql = "SELECT resourceNumber FROM Resources WHERE facilityID = %s AND status = %s"
                sqlVar = (facilityID,"Available")

                #Run SQL Query
                cur.execute(sql, sqlVar)
                result = cur.fetchall()

                for i in range(0,len(result)):

                    tablenameRes = tablename + str(result[i][0])

                    #Create SQL Query
                    sql = "SELECT sessionRange, slotID FROM {} WHERE date = %s AND status = 'free'".format(tablenameRes)
                    sqlVar = (date,)

                    #Run SQL Query
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
            
            return render_template('booking2.html', sessions1 = sessions1, sessions2 = sessions2, facilityName = facilityName, facilityID = facilityID, date = date, sessions1ids = sessions1ids, sessions2ids = sessions2ids, tbl = tablename)

        if "book1" in request.form:
            date = request.form.get('date')
            session = request.form.get('r1choice')
            sessionid = request.form.get('r1choiceID')
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

                #Create SQL Query
                sql = "INSERT INTO `Booking`(`resourceNumber`, `facilityID`, `useStart`, `useEnd`, `useDate`, `userID`) VALUES (%s,%s,%s,%s,%s,%s)"
                sqlVar = (resourceNum, facilityID, start, end, date, g.user.id)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()

                #Create SQL Query
                sql = "SELECT MAX(bookingID) FROM Booking"
                #Run SQL Query
                cur.execute(sql,)
                result = cur.fetchone()
                bookingID = result[0]

                #Create SQL Query
                sql = "UPDATE {} SET status = 'booked', bookingID = %s WHERE slotID = %s".format(tablename)
                sqlVar = (bookingID, sessionID)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()

                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")

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

                #Create SQL Query
                sql = "INSERT INTO `Booking`(`resourceNumber`, `facilityID`, `useStart`, `useEnd`, `useDate`, `userID`) VALUES (%s,%s,%s,%s,%s,%s)"
                sqlVar = (resourceNum, facilityID, start, end, date, g.user.id)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()

                #Create SQL Query
                sql = "SELECT MAX(bookingID) FROM Booking"
                #Run SQL Query
                cur.execute(sql,)
                result = cur.fetchone()
                bookingID = result[0]

                #Create SQL Query
                sql = "UPDATE {} SET status = 'booked', bookingID = %s WHERE slotID = %s".format(tablename)
                sqlVar = (bookingID, sessionID)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()

                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")

        
    return render_template('booking1.html', facilityName = facilitynames, facilityids = facilityids, today = dateToday, endRange = nextMonthString)

#View Bookings
@app.route('/viewbooking', methods = ['post', 'get'])
def viewbooking():
    if not g.user:
        return redirect('/SFMS/login')

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


    if(request.method == 'POST'):
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
                sql = "SELECT * FROM Booking WHERE (useDate = %s) AND WHERE userID = %s"
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

            for i in range(0, len(userids)):
                sql = "SELECT username from SFMSUser WHERE userID = %s"
                sqlVar = (userids[i],)
                cur.execute(sql,sqlVar)
                result = cur.fetchone()
                usernames.append(result[0])

            for i in range(0, len(resourceNums)):
                sql = "SELECT resourceName from Resources WHERE facilityID = %s AND resourceNumber = %s"
                sqlVar = (facilityids[i], resourceNums[i],)
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

    return render_template('manageBooking.html', bookingids = bookingids, bookingdatetime = bookingdatetime, resourcenames = resourcenames, facilitynames = facilitynames, starttimes = starttimes, endtimes = endtimes, usedate = usedate, usernames = usernames)


#Facility Management
@app.route('/facilitymanagement', methods=['post','get'])
def newFacility():
    if not g.user:
        return redirect('/SFMS/login')
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    facilities = []

    try:
        #Connect to DB
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()

        #Create SQL Query
        sql = "SELECT facilityName FROM Facility"

        #Run SQL Query
        cur.execute(sql,)
        result = cur.fetchall()
        cur.close()
        conn.close()

        for i in range(0,len(result)):
            facilities.append(result[i][0])

    except mariadb.Error as e:
        print(f"Error: {e}")

    resourceName = []
    status = []
    #Retrieve POST Request Data
    if (request.method == 'POST'): 

        if 'addFacility' in request.form:
            facilityName = request.form.get('facilityName')
            resourceName.append(request.form.get('r1'))
            resourceName.append(request.form.get('r2'))
            status.append(request.form.get('status1'))
            status.append(request.form.get('status2'))
            sessionLength = request.form.get('session')
            gracePeriod = request.form.get('grace')

            sessionTimes, dates = generateSessions(sessionLength,gracePeriod, dateToday)

            if (len(facilityName.split()) == 1):
                facilityName = facilityName.rstrip() + " Facility"

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Create SQL Query
                sql = "INSERT INTO Facility (facilityName, sessionLength, gracePeriod) VALUES (%s, %s, %s)"
                sqlVar = (facilityName, sessionLength, gracePeriod)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()

                #Create SQL Query
                sql = "SELECT MAX(facilityID) FROM Facility"

                #Run SQL Query
                cur.execute(sql,)
                result = cur.fetchone()

                facilityID = result[0]

                for i in range(0, len(resourceName)):
                    resourceNum = i+1
                    #Create SQL Query
                    sql = "INSERT INTO Resources (resourceName, resourceNumber, facilityID, status) VALUES (%s, %s, %s, %s)"
                    sqlVar = (resourceName[i], resourceNum, facilityID, status[i])

                    #Run SQL Query
                    cur.execute(sql, sqlVar)
                    conn.commit()

                    tableVar = facilityName.split(" ")
                    tablename = tableVar[0][0] + tableVar[1][0] + "R" + str(resourceNum)

                    sql = "DROP TABLE IF EXISTS {}".format(tablename)
                    
                    #Run SQL Query
                    cur.execute(sql,)
                    conn.commit()

                    sql = "CREATE TABLE {} (slotID int(11) AUTO_INCREMENT NOT NULL PRIMARY KEY, sessionRange varchar(255) NOT NULL, bookingID int(11), status varchar(10) NOT NULL DEFAULT 'free', date date NOT NULL)".format(tablename)
                    
                    #Run SQL Query
                    cur.execute(sql, )
                    conn.commit()

                    for i in dates:

                        for j in sessionTimes:
                            sql = "INSERT INTO {} (sessionRange, date) VALUES (%s, %s)".format(tablename)
                            sqlVar = (j, i)

                            #Run SQL Query
                            cur.execute(sql,sqlVar)
                            conn.commit()

                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")

            return redirect('/SFMS/facilitymanagement')

        if 'remove' in request.form:
            facilityName = request.form.get('facilityName')

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Create SQL Query
                sql = "DELETE FROM Facility WHERE facilityName = %s"
                sqlVar = (facilityName,)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")

            return redirect('/SFMS/facilitymanagement')

    return render_template("manageFacility.html", facilities = facilities)

#Resource Management
@app.route('/resourcemanagement', methods=['post','get'])
def manageResources():
    if not g.user:
        return redirect('/SFMS/login')
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    facilityName = ""
    resources = ""
    resourceNum = ""
    status = ""


    if (request.method == 'POST'):

        if "manage" in request.form:
            facilityName = request.form.get('facilityName')
            resources = []
            resourceNum = []
            status = []

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Create SQL Query
                sql = "SELECT resourceName, resourceNumber, status FROM Resources WHERE facilityID = (SELECT facilityID FROM Facility WHERE facilityName = %s)"
                sqlVar = (facilityName,)

                #Run SQL Query
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
        
        if "updateStatus" in request.form:
            facilityName = request.form.get('facilityName')
            resourceNum = request.form.get('resourceNum')
            status = request.form.get('status')

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Create SQL Query
                sql = "UPDATE Resources SET status = %s WHERE (facilityID = (SELECT facilityID FROM Facility WHERE facilityName = %s)) AND (resourceNumber = %s)"
                sqlVar = (status, facilityName, resourceNum)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
                
            except mariadb.Error as e:
                print(f"Error: {e}")
            return redirect('/SFMS/resourcemanagement')

        if "rename" in request.form:
            facilityName = request.form.get('facilityName')
            resourceNum = request.form.get('resourceNum')
            newresourceName = request.form.get('newresourceName')

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Create SQL Query
                sql = "UPDATE Resources SET resourceName = %s WHERE (facilityID = (SELECT facilityID FROM Facility WHERE facilityName = %s)) AND (resourceNumber = %s)"
                sqlVar = (newresourceName, facilityName, resourceNum)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
                
            except mariadb.Error as e:
                print(f"Error: {e}")
            return redirect('/SFMS/resourcemanagement')

    return render_template('manageResource.html', facilityName = facilityName, resources = resources, resourceNum = resourceNum, status = status)

#User Management
@app.route('/usermanagement', methods=['post','get'])
def newUser():
    if not g.user:
        return redirect('/SFMS/login')
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    fname = []
    lname = []
    usernames = []

    try:
        #Connect to DB
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()

        #Create SQL Query
        sql = "SELECT firstName, lastName, username FROM SFMSUser WHERE userType != 'admin' AND userType != 'SYSTEM' AND status != 'inactive'"

        #Run SQL Query
        cur.execute(sql,)
        result = cur.fetchall()
        cur.close()
        conn.close()


        for i in range(0,len(result)):
            fname.append(result[i][0])
            lname.append(result[i][1])
            usernames.append(result[i][2])

    except mariadb.Error as e:
        print(f"Error: {e}")

    
    
    #Retrieve POST Request Data
    if (request.method == 'POST'): 
        
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
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Create SQL Query
                sql = "INSERT INTO SFMSUser (firstName, lastName, username, userType, userAddress, email, telephone, sesame, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                sqlVar = (firstname, lastname, username, usertype, useraddress, useremail, telephone, hashedPassword, "active")

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")

            return redirect('/SFMS/usermanagement')

        if "deactivate" in request.form:

            username = request.form.get('username')

            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Create SQL Query
                sql = "UPDATE SFMSUser SET status = %s WHERE username = %s"
                sqlVar = ("inactive",username)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()

                sql = "UPDATE Cards SET userID = 0 WHERE userID = (SELECT userID FROM SFMSUser WHERE username = %s)"
                sqlVar = (username,)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()

            except mariadb.Error as e:
                print(f"Error: {e}")

            return redirect('/SFMS/usermanagement')


    return render_template("manageUser.html", firstname = fname, lastname = lname, username = usernames)

#Assign RFID Card to Member
@app.route('/cardmanagement', methods = ['post', 'get'])
def assign():

    #Check if a user is logged in
    if not g.user:
        return redirect('/SFMS/login')

    #Check if logged in user is Admin
    if g.user.userType != "admin":
        return redirect('/SFMS/')
    users = []
    newcards = []
    usedcards = []

    try:

        #Connect to DB
        conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
        cur = conn.cursor()


        #Select all users
        sql = "SELECT username FROM SFMSUser"

        #Run SQL Query
        cur.execute(sql,)
        result = cur.fetchall()

        #Add all usernames in database to list
        for i in range(0,len(result)):
            users.append(result[i][0])

        #Select Unassigned Cards
        sql = "SELECT * FROM Cards WHERE userID = 0"

        #Run SQL Query
        cur.execute(sql,)
        result = cur.fetchall()

        #Add all unassigned cards to list
        for i in range(0,len(result)):
            newcards.append(result[i][1])

        #Select all assigned Cards
        sql = "SELECT * FROM Cards WHERE userID != 0"

        #Run SQL Query
        cur.execute(sql,)
        result = cur.fetchall()

        #Add all assigned cards to list
        for i in range(0,len(result)):
            usedcards.append(result[i][1])

        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Error: {e}")

    #Check for POST request from webpage
    if(request.method =='POST'):

        #If admin wants to assign an unused card to a user
        if 'assignNew' in request.form:

            username = request.form.get('username')
            chosenRFID = request.form.get('newcards')
            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Change the user associated with an RFID card to the user selected on the webpage
                sql = "UPDATE Cards SET userID = (SELECT userID FROM SFMSUser WHERE username = %s) WHERE cardID = %s"
                sqlVar = (username, chosenRFID)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
                return redirect('/SFMS/cardmanagement')

            except mariadb.Error as e:
                print(f"Error: {e}")

        #If admin wants to a reassign a card from one user to another
        if 'reassign' in request.form:

            username = request.form.get('username')
            chosenRFID = request.form.get('usedcards')
            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                sql = "UPDATE Cards SET userID = (SELECT userID FROM SFMSUser WHERE username = %s) WHERE cardID = %s"
                sqlVar = (username, chosenRFID)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
                return redirect('/SFMS/cardmanagement')

            except mariadb.Error as e:
                print(f"Error: {e}")

        #If admin wants to add new card to system
        if 'addNew' in request.form:
            rfid = request.form.get('addcard')
            try:
                #Connect to DB
                conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
                cur = conn.cursor()

                #Change the user associated with an RFID card to the user selected on the webpage
                sql = "INSERT INTO Cards (userID, cardID) VALUES (%s, %s)"
                sqlVar = ("0",rfid)

                #Run SQL Query
                cur.execute(sql, sqlVar)
                conn.commit()
                cur.close()
                conn.close()
                return redirect('/SFMS/cardmanagement')

            except mariadb.Error as e:
                print(f"Error: {e}")


    return render_template("manageCard.html", users = users, newcards = newcards, usedcards = usedcards)

#System Logs
@app.route('/systemlogs', methods=['post','get'])
def systemlogs():
    if not g.user:
        return redirect('/SFMS/login')
    if g.user.userType != "admin":
        return redirect('/SFMS/')

    firstName = []
    lastName = []
    facilityID = []
    facilityName = []
    readingTime = []
    userids = []
    rfid = []
    dateString1 = dateToday + " 00:00:00"
    dateString2 = dateToday + " 23:59:59"
    weekString = lastWeekString + " 00:00:00"
    monthString = lastMonthString + " 00:00:00"

    if(request.method == 'POST'):
        logRange = request.form.get('range')

        try:
            #Connect to DB
            conn = mariadb.connect(user="webclient", password="wc_boss5", host="localhost", database="SFM")
            cur = conn.cursor()

            if (logRange == 'today'):
                sql = "SELECT facilityID, rfid, reading_time FROM SensorData WHERE reading_time BETWEEN %s AND %s"
                sqlVar = (dateString1, dateString2)

            if (logRange == 'week'):
                sql = "SELECT facilityID, rfid, reading_time FROM SensorData WHERE reading_time BETWEEN %s AND %s"
                sqlVar = (weekString, dateString1)

            if (logRange == 'month'):
                sql = "SELECT facilityID, rfid, reading_time FROM SensorData WHERE reading_time BETWEEN %s AND %s"
                sqlVar = (monthString, dateString1)
            

            #Run SQL Query
            cur.execute(sql,sqlVar)
            result = cur.fetchall()

            for i in range(0,len(result)):
                facilityID.append(result[i][0])
                rfid.append(result[i][1])
                readingTime.append(result[i][2])

            for i in range(0,len(rfid)):

                sql = "SELECT userID FROM Cards WHERE userID = %s"
                sqlVar = (rfid[i],)

                #Run SQL Query
                cur.execute(sql,sqlVar)
                result = cur.fetchall()

                for j in range(0,len(result)):
                    userids.append(result[j][0])

            for i in range(0,len(userids)):

                sql = "SELECT firstName, lastName FROM SFMSUser WHERE userID = %s"
                sqlVar = (userids[i],)

                #Run SQL Query
                cur.execute(sql,sqlVar)
                result = cur.fetchall()

                for j in range(0,len(result)):
                    firstName.append(result[j][0])
                    lastName.append(result[j][1])

            for i in range(0, len(facilityID)):

                sql = "SELECT facilityName FROM Facility WHERE facilityID = %s"
                sqlVar = (facilityID[i],)

                #Run SQL Query
                cur.execute(sql,sqlVar)
                result = cur.fetchall()

                for j in range(0,len(result)):
                    facilityName.append(result[j][0])

            cur.close()
            conn.close()

        except mariadb.Error as e:
            print(f"Error: {e}")

    return render_template('systemLog.html', firstName = firstName, lastName = lastName ,facilityName = facilityName, readingTime = readingTime)


#Verify Booking
@app.route('/verify', methods=['post', 'get'])
def verifyBooking():

    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.today().time()

    if (request.method == 'POST'):
        name = request.form.get('sensor')
        facility = request.form.get('facilityID')
        rfid = request.form.get('rfid')

        try:
	    #Connect to DB
            conn = mariadb.connect(user="esp32", password="esp_boss5", host="localhost", database="SFM")
            cur = conn.cursor()

	    #Create SQL Query to log a facility access attempt
            sql = "INSERT INTO SensorData (sensor, facilityID, rfid) VALUES (%s, %s, %s)"
            sqlVar = (name, facility, rfid)

	    #Run SQL Query
            cur.execute(sql, sqlVar)
            conn.commit()

            #Create SQL Query to check for a booking
            sql = "SELECT resourceID, useStart, useEnd FROM Booking WHERE userID = (SELECT userID FROM Cards WHERE cardID = %s) AND useDate = %s AND facilityID = %s"
            sqlVar = (rfid, today, facility)

            #Run SQL Query
            cur.execute(sql, sqlVar)
            result = cur.fetchall()

            cur.close()
            conn.close()

            if not result:
                message = "0"
                return  message, 200

            start = datetime.datetime.strptime(result[-1][1], '%H:%M:%S').time()
            end = datetime.datetime.strptime(result[-1][2], '%H:%M:%S').time()

            endVar = result[-1][2]
            nowVar = datetime.datetime.now().strftime("%H:%M:%S")

            resource = result[-1][0]
            timeVar = timeLeft(nowVar, endVar)

            if (start <= now) and (now <= end):
                message = "1," + str(resource) + "," + str(timeVar)
            else:
                message = "0"
        except mariadb.Error as e:
            print(f"Error: {e}")
    return message, 200


#Run Server
if __name__ == "__main__":
    app.run(debug=True)

