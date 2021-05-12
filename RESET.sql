DROP TABLE IF EXISTS Booking;
create table Booking(

	bookingID int(10) NOT NULL UNIQUE AUTO_INCREMENT,
	bookDateTime datetime,
	resourceNumber int (50) NOT NULL UNIQUE,
    facilityID int (10) NOT NULL UNIQUE,
    useStart varchar (10) NOT NULL , -- type should probably be time
    useEnd varchar (10) NOT NULL, -- type should probably be time
    useDate date,
    userID int (10) NOT NULL ,
    status varchar (25) NOT NULL DEFAULT 'Upcoming',
    primary key(bookingID)
	
);

 
DROP TABLE IF EXISTS Cards;
create table Cards(
	userID int(10) NOT NULL UNIQUE,
	CardID varchar(15) NOT NULL UNIQUE, 
    primary key (CardID) -- type should probably be INT
	
);


DROP TABLE IF EXISTS Facility;
create table Facility (
	facilityName varchar(10) NOT NULL UNIQUE, 
	facilityID int(10) NOT NULL AUTO_INCREMENT,
	sessionLength int(11) NOT NULL, 
    gracePeriod int(11) NOT NULL,
	primary key (facilityID)
	
);


DROP TABLE IF EXISTS SensorData; 
create table SensorData (
	id int(6) NOT NULL AUTO_INCREMENT , 
	sensor varchar(30) NOT NULL , 
	facilityID int(50) NOT NULL,
    rfid varchar (10) NOT NULL,
    resourceNumber int (11) NOT NULL,
    reading_time timestamp,
	primary key (id)
	
);


DROP TABLE IF EXISTS Resources; 
create table Resource (
	resourceID int(50) NOT NULL AUTO_INCREMENT , 
	resourceName varchar(500) NOT NULL ,
	resourceNumber int (11) NOT NULL, 
	facilityID int(50) NOT NULL,
    status varchar (15) NOT NULL,
	primary key (resourceID)
	
);


DROP TABLE IF EXISTS SFMSUser; 
create table SFMSUser (
	userID int(10) NOT NULL UNIQUE AUTO_INCREMENT , 
	firstName varchar(30) NOT NULL ,
	lastName varchar(30) NOT NULL, 
	username varchar(30) NOT NULL,
    userType varchar (15) NOT NULL,
    userAddress varchar (500) not NULL,
    email varchar(30) NOT NULL,
    telephone varchar(30) NOT NULL,
    sesame varchar(500) NOT NULL,
    status varchar (20) NOT NULL,
    image image,
	primary key (userID, username)
	
);

DROP TABLE IF EXISTS Resources; 
create table Resource (
	firstName varchar(30)NOT NULL , 
	lastName varchar(30) NOT NULL ,
	facilityID int(50) NOT NULL,
    reading_time timestamp,
	primary key (facilityID)
	
);

DROP TABLE IF EXISTS FFR1; -- FIELDS NEED TO BE EDITED
create table FFR1 (
	resourceID int(50) NOT NULL AUTO_INCREMENT , 
	resourceName varchar(500) NOT NULL ,
	resourceNumber int (11) NOT NULL, 
	facilityID int(50) NOT NULL,
    status varchar (15) NOT NULL,
	primary key (resourceID)
	
);

DROP TABLE IF EXISTS FFR2; -- FIELDS NEED TO BE EDITED
create table FFR2 (
	resourceID int(50) NOT NULL AUTO_INCREMENT , 
	resourceName varchar(500) NOT NULL ,
	resourceNumber int (11) NOT NULL, 
	facilityID int(50) NOT NULL,
    status varchar (15) NOT NULL,
	primary key (resourceID)
	
);


INSERT INTO Booking (bookingID,resourceNumber,facilityID,userID,status) VALUES (1,1,1,3,"Upcoming");


INSERT INTO Cards (userID,cardID) VALUES (3,'245DC29');


INSERT INTO Facility (facilityName,facilityID,sessionLength, gracePeriod) VALUES ('Football Facility',1,1,0);





INSERT INTO Resources (resourceID,resourceName,resourceNumber,facilityID,status) VALUES (1,'Field 1',1, 1, "Upcoming");



INSERT INTO SFMSUser (userID,firstName,lastName,username,userType,userAddress,email,telephone,sesame,status) VALUES (1,'SYSTEM','SYSTEM','SYSTEM','SYSTEM','SYSTEM','SYSTEM','SYSTEM', 'd621c1a7169f2ca51bc8674da52e9572178a66a1dde88da24da78fe4951703f9','active');

INSERT INTO SFMSUser (userID,firstName,lastName,username,userType,userAddress,email,telephone,sesame,status) VALUES (2,'admin','admin','admin','admin','admin','sfmsadmin@gmail.com','8767323646', 'd621c1a7169f2ca51bc8674da52e9572178a66a1dde88da24da78fe4951703f9','active');

INSERT INTO SFMSUser (userID,firstName,lastName,username,userType,userAddress,email,telephone,sesame,status) VALUES (3,'John','Brown','jbrown','member','1 Gibraltar Avenue',' jbrown@email.com','8761234567', '62b8f6c5baa5edd2d018020a6d17a2a37fbf727eaa3f1abdb5502d4113adf2a9','active');


