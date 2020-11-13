ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'pass123';

drop database if exists db;
create database db;
use db;

SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

CREATE TABLE User
(
  User_Name varchar (40),
  User_ID varchar(40),
  Phone_Number varchar(40) not null primary key
);

CREATE TABLE Channel
(
  Channel_ID   varchar(40) not null primary key,
  Channel_Link varchar(50),
  Channel_Name varchar(40) not null,
  Channel_Dest varchar(50)
);

CREATE TABLE MGroup
(
  Group_ID   varchar(40) not null primary key,
  Group_Link varchar(50),
  Group_Name varchar(40) not null,
  Group_Dest varchar(50)
);

CREATE TABLE Message
(
  Text varchar(200) not null ,
  Send_Time TIME not null,
  Message_ID VARCHAR(40) not null primary key,
  Sender_Phone VARCHAR(40) NOT NULL,
  Send_Date DATE not null,
  FOREIGN KEY (Sender_Phone) REFERENCES User(Phone_Number)
);

CREATE TABLE Channel_Messages(
  Channel_ID varchar(40) not null ,
  Message_ID varchar(40) not null ,
  Number_Of_Seens int not null ,
  FOREIGN KEY (Channel_ID) REFERENCES Channel(Channel_ID),
  FOREIGN KEY (Message_ID) REFERENCES Message(Message_ID)
);

CREATE TABLE Group_Message(
  Group_ID varchar(40) not null ,
  Message_ID varchar(40) not null ,
  Number_Of_Seens int not null ,
  FOREIGN KEY (Group_ID) REFERENCES MGroup(Group_ID),
  FOREIGN KEY (Message_ID) REFERENCES Message(Message_ID)
);

CREATE TABLE Receiver_Message(
  Receiver_Phone_Number varchar(40) not null ,
  Message_ID varchar(40) not null,
  Seen boolean not null ,
  FOREIGN KEY (Receiver_Phone_Number) REFERENCES User(Phone_Number),
  FOREIGN KEY (Message_ID) REFERENCES Message(Message_ID)
);

CREATE TABLE Blocked_User
(
  Block_Date DATE not null,
  Blocker_Number varchar(40) not null ,
  Blocked_Number varchar(40) not null ,
  FOREIGN KEY (Blocker_Number) REFERENCES User(Phone_Number),
  FOREIGN KEY (Blocked_Number) REFERENCES User(Phone_Number)
);

CREATE TABLE User_Settings
(
  Bio varchar(100),
  Self_Destruct int,
  Two_Step_Password varchar(40),
  User_Phone varchar(40) not null,
  FOREIGN KEY (User_Phone) REFERENCES User(Phone_Number)
);

CREATE TABLE Channel_Settings
(
  Bio varchar(100),
  Self_Destruct int,
  Two_Step_Password varchar(40),
  Channel_ID varchar(40) not null,
  Creator_Phone VARCHAR(40) NOT NULL,
  FOREIGN KEY (Channel_ID) REFERENCES Channel(Channel_ID),
  FOREIGN KEY (Creator_Phone) REFERENCES USER(Phone_Number)
);

CREATE TABLE Group_Settings
(
  Bio varchar(100),
  Self_Destruct int,
  Two_Step_Password varchar(40),
  Group_ID varchar(40) not null,
  Creator_Phone VARCHAR(40) NOT NULL,
  FOREIGN KEY (Group_ID) REFERENCES MGroup(Group_ID),
  FOREIGN KEY (Creator_Phone) REFERENCES USER(Phone_Number)
);

CREATE TABLE User_Session
(
  Creation_Date DATE not null,
  Device varchar(40),
  Last_Date double not null,
  IP varchar(40),
  OS varchar(40),
  User_Phone varchar(40) not null,
  FOREIGN KEY (User_Phone) REFERENCES User(Phone_Number)
);

CREATE TABLE Channel_Members
(
  Member_Number varchar(40) not null,
  Channel_ID varchar(40) not null ,
  FOREIGN KEY (Member_Number) REFERENCES User(Phone_Number),
  FOREIGN KEY (Channel_ID) REFERENCES Channel(Channel_ID)
);

CREATE TABLE Group_Enrollment
(
  Member_Phone varchar(40) not null ,
  Group_ID varchar(40) not null,
  FOREIGN KEY (Member_Phone) REFERENCES User(Phone_Number),
  FOREIGN KEY (Group_ID) REFERENCES MGroup(Group_ID)
);

CREATE TABLE Seen_Messages(
  Message_ID varchar(40) not null ,
  User_Phone varchar(40) not null,
FOREIGN KEY (Message_ID) REFERENCES Message(Message_ID),
FOREIGN KEY (User_Phone) REFERENCES User(Phone_Number)
);



INSERT INTO USER VALUES ('System',NULL,'SYS')

