drop database if exists db;
create database db;
use db;


CREATE TABLE User
(
  User_Name varchar (10) not null,
  User_ID varchar(10) not null primary key ,
  Phone_Number varchar(10) not null
);

CREATE TABLE Channel
(
  Channel_ID   varchar(10) not null primary key,
  Channel_Link varchar(50) not null,
  Channel_Name varchar(20) not null,
  Channel_Dest varchar(50) not null
);

CREATE TABLE MGroup
(
  Group_ID   varchar(10) not null primary key,
  Group_Link varchar(50) not null,
  Group_Name varchar(20) not null,
  Group_Dest varchar(50) not null
);

CREATE TABLE Message
(
  Text varchar(200) not null ,
  Send_Time TIME not null,
  Message_ID VARCHAR(10) not null primary key,
  Sender_ID VARCHAR(10) NOT NULL
);

CREATE TABLE Channel_Messages(
  Channel_ID varchar(10) not null ,
  Message_ID varchar(10) not null ,
  Number_Of_Seens int not null ,
  FOREIGN KEY (Channel_ID) REFERENCES Channel(Channel_ID),
  FOREIGN KEY (Message_ID) REFERENCES Message(Message_ID)
);

CREATE TABLE Group_Message(
  Group_ID varchar(10) not null ,
  Message_ID varchar(10) not null ,
  Number_Of_Seens int not null ,
  FOREIGN KEY (Group_ID) REFERENCES MGroup(Group_ID),
  FOREIGN KEY (Message_ID) REFERENCES Message(Message_ID)
);

CREATE TABLE Receiver_Message(
  Receiver_ID varchar(10) not null ,
  Message_ID varchar(10) not null,
  Seen boolean not null ,
  FOREIGN KEY (Receiver_ID) REFERENCES User(User_ID),
  FOREIGN KEY (Message_ID) REFERENCES Message(Message_ID)
);

CREATE TABLE Blocked_User
(
  Block_Date DATE not null,
  Blocker_ID varchar(10) not null ,
  Blocked_ID varchar(10) not null ,
  FOREIGN KEY (Blocker_ID) REFERENCES User(User_ID),
  FOREIGN KEY (Blocked_ID) REFERENCES User(User_ID)
);

CREATE TABLE User_Settings
(
  Bio varchar(100) not null,
  Self_Destruct boolean not null,
  Two_Step_Password varchar(20) not null,
  User_ID varchar(10) not null,
  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE Channel_Settings
(
  Bio varchar(100) not null,
  Self_Destruct boolean not null,
  Two_Step_Password varchar(20) not null,
  Channel_ID varchar(10) not null,
  FOREIGN KEY (Channel_ID) REFERENCES Channel(Channel_ID)
);

CREATE TABLE Group_Settings
(
    Bio varchar(100) not null,
  Self_Destruct boolean not null,
  Two_Step_Password varchar(20) not null,
  Group_ID varchar(10) not null,
  FOREIGN KEY (Group_ID) REFERENCES MGroup(Group_ID)
);

CREATE TABLE User_Session
(
  Creation_Date DATE not null,
  Device varchar(20) not null,
  Last_Date DATE not null,
  IP varchar(20) not null primary key,
  OS varchar(15) not null,
  User_ID varchar(10) not null ,
  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE Channel_Members
(
  Member_ID varchar(10) not null,
  Channel_ID varchar(10) not null ,
  FOREIGN KEY (Member_ID) REFERENCES User(User_ID),
  FOREIGN KEY (Channel_ID) REFERENCES Channel(Channel_ID)
);

CREATE TABLE Group_Enrollment
(
  Member_ID varchar(10) not null ,
  Group_ID varchar(10) not null,
  FOREIGN KEY (Member_ID) REFERENCES User(User_ID),
  FOREIGN KEY (Group_ID) REFERENCES MGroup(Group_ID)
);

CREATE TABLE Seen_Messages(
  Message_ID varchar(10) not null ,
  User_ID varchar(10) not null,
  FOREIGN KEY (Message_ID) REFERENCES Message(Message_ID),
  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

INSERT INTO User VALUES ('Koosha','mrkooshaj','9120966961');
INSERT INTO User VALUES ('Soroosh','Sorooshbsl','9217468301');
INSERT INTO User VALUES ('Ashkan','Ashkansoli','9135454861');
INSERT INTO User VALUES ('AmirHosein','abahram77','9197499171');
INSERT INTO User VALUES ('Ali','AATeshnizi','9136060360');
INSERT INTO User VALUES ('Amin','amnra','9124798394');
INSERT INTO User VALUES ('Ali','bahjatia','9196855227');
INSERT INTO User VALUES ('Mahbod','MhbdM','9126975750');

INSERT INTO Channel VALUES ('konkur','https://t.me/kooshakonkur','Official Koosha','');
INSERT INTO Channel VALUES ('emoji','https://t.me/Kooshaemoji','Emoji & Gif Analysis','');
INSERT INTO Channel VALUES ('ostrich','https://t.me/khashmeshotormorgh','Same Photo Ostrich','');
INSERT INTO Channel VALUES ('daeiamoo','https://t.me/daeiamoo','Daei Amoo Recognize','');
INSERT INTO Channel VALUES ('Sport','https://t.me/sharifsports','Sharif Sports','');
INSERT INTO Channel VALUES ('Chelsea','https://t.me/ChelseaIranianFans','Chelsea Iranian Fans','');

INSERT INTO MGroup VALUES ('kharrazi','https://t.me/joinchat/BWKOelGT-GLnwP_fpRVrIQ','OS Kharrazi','');
INSERT INTO MGroup VALUES ('rivadeh','https://t.me/joinchat/BWKOekxtYnQnQgv77u_BwA','DB Rivadeh','');
insert INTO MGroup VALUES ('rohban','https://t.me/joinchat/ByukXU823T4ZPpe23Bp8-g','AI Rohban','');
INSERT INTO MGroup VALUES ('zarrabi','https://t.me/joinchat/BWKOekjzbNcYz4ohz5gVBQ','DA Zarrabi','');
INSERT INTO MGroup VALUES ('amini','https://t.me/joinchat/BWKOekWIu0LBfnNpCYxV5Q','DB Amini','');
INSERT INTO MGroup VALUES ('koohi','https://t.me/joinchat/BWKOelI1RYMUcOwE7UawVA','Madar Koohi','');

INSERT INTO Channel_Members VALUES ('mrkooshaj','konkur');
INSERT INTO Channel_Members VALUES ('mrkooshaj','emoji');
INSERT INTO Channel_Members VALUES ('mrkooshaj','ostrich');
INSERT INTO Channel_Members VALUES ('mrkooshaj','daeiamoo');
INSERT INTO Channel_Members VALUES ('mrkooshaj','Sport');
INSERT INTO Channel_Members VALUES ('mrkooshaj','Chelsea');

INSERT INTO Channel_Members VALUES ('Sorooshbsl','konkur');
INSERT INTO Channel_Members VALUES ('Sorooshbsl','emoji');
INSERT INTO Channel_Members VALUES ('Sorooshbsl','Sport');

INSERT INTO Channel_Members VALUES ('Ashkansoli','konkur');
INSERT INTO Channel_Members VALUES ('Ashkansoli','ostrich');
INSERT INTO Channel_Members VALUES ('Ashkansoli','daeiamoo');
INSERT INTO Channel_Members VALUES ('abahram77','konkur');
INSERT INTO Channel_Members VALUES ('abahram77','Sport');
INSERT INTO Channel_Members VALUES ('abahram77','emoji');
INSERT INTO Channel_Members VALUES ('AATeshnizi','konkur');
INSERT INTO Channel_Members VALUES ('AATeshnizi','ostrich');
INSERT INTO Channel_Members VALUES ('amnra','ostrich');
INSERT INTO Channel_Members VALUES ('amnra','Chelsea');
INSERT INTO Channel_Members VALUES ('amnra','emoji');
INSERT INTO Channel_Members VALUES ('amnra','daeiamoo');
INSERT INTO Channel_Members VALUES ('bahjatia','daeiamoo');
INSERT INTO Channel_Members VALUES ('bahjatia','emoji');
INSERT INTO Channel_Members VALUES ('bahjatia','Sport');

INSERT INTO Group_Enrollment VALUES ('mrkooshaj','kharrazi');
INSERT INTO Group_Enrollment VALUES ('mrkooshaj','rivadeh');
INSERT INTO Group_Enrollment VALUES ('mrkooshaj','zarrabi');
INSERT INTO Group_Enrollment VALUES ('Sorooshbsl','rivadeh');
INSERT INTO Group_Enrollment VALUES ('Sorooshbsl','rohban');
INSERT INTO Group_Enrollment VALUES ('Sorooshbsl','zarrabi');
INSERT INTO Group_Enrollment VALUES ('Ashkansoli','rivadeh');
INSERT INTO Group_Enrollment VALUES ('Ashkansoli','zarrabi');
INSERT INTO Group_Enrollment VALUES ('Ashkansoli','rohban');
INSERT INTO Group_Enrollment VALUES ('Ashkansoli','koohi');
INSERT INTO Group_Enrollment VALUES ('abahram77','rivadeh');
INSERT INTO Group_Enrollment VALUES ('abahram77','zarrabi');
INSERT INTO Group_Enrollment VALUES ('abahram77','koohi');
INSERT INTO Group_Enrollment VALUES ('AATeshnizi','rivadeh');
INSERT INTO Group_Enrollment VALUES ('amnra','rohban');
INSERT INTO Group_Enrollment VALUES ('amnra','koohi');
INSERT INTO Group_Enrollment VALUES ('bahjatia','rohban');
INSERT INTO Group_Enrollment VALUES ('bahjatia','kharrazi');
INSERT INTO Group_Enrollment VALUES ('MhbdM','rohban');
INSERT INTO Group_Enrollment VALUES ('MhbdM','amini');

INSERT INTO Message VALUES ('Salam', 1, 'id_a', 'Sorooshbsl');
INSERT INTO Message VALUES ('Chetori?', 2, 'id_b', 'mrkooshaj');
INSERT INTO Message VALUES ('MerC', 3, 'id_c', 'Sorooshbsl');
INSERT INTO Receiver_Message VALUES ('mrkooshaj', 'id_a', TRUE );
INSERT INTO Receiver_Message VALUES ('Sorooshbsl', 'id_b', FALSE );
INSERT INTO Receiver_Message VALUES ('mrkooshaj', 'id_c', FALSE );

INSERT INTO Message VALUES ('Che khabara?', 20, 'id_d', 'Sorooshbsl');
INSERT INTO Message VALUES ('hichi', 28, 'id_e', 'Ashkansoli');
INSERT INTO Message VALUES ('Mamnoon', 30, 'id_f', 'Ashkansoli');
INSERT INTO Message VALUES ('Soltan!', 33, 'id_f1', 'Ashkansoli');
INSERT INTO Receiver_Message VALUES ('Ashkansoli', 'id_d', TRUE );
INSERT INTO Receiver_Message VALUES ('Sorooshbsl', 'id_e', FALSE );
INSERT INTO Receiver_Message VALUES ('Sorooshbsl', 'id_f', FALSE );
INSERT INTO Receiver_Message VALUES ('Sorooshbsl', 'id_f1', FALSE );

INSERT INTO Message VALUES ('midterm keie?', 17, 'id_g', 'Ashkansoli');
INSERT INTO Group_Message VALUES ('rohban', 'id_g', 0);
INSERT INTO Message VALUES ('midterm keieiiiii?', 17, 'id_g12', 'Ashkansoli');
INSERT INTO Group_Message VALUES ('rohban', 'id_g12', 0);
INSERT INTO Message VALUES ('midterm keieiiiiiii?', 17, 'id_g123', 'Ashkansoli');
INSERT INTO Group_Message VALUES ('rohban', 'id_g123', 0);
INSERT INTO Message VALUES ('man darso nadaram :)))', 19, 'id_h', 'MhbdM');
INSERT INTO Group_Message VALUES ('rohban', 'id_h', 0);


INSERT INTO User_Settings VALUES ('3rd Konkur 95, Chess Player',True,'kjkjkj','mrkooshaj');
INSERT INTO User_Settings VALUES ('2nd Mantaghe 2 sibiloo',FALSE ,'sbsl','sorooshbsl');
INSERT INTO User_Settings VALUES ('Ping Pong Player (PPP)',True,'behramiv','abahram77');
INSERT INTO User_Settings VALUES ('From Esfahan :)',True,'zoranp','Ashkansoli');
INSERT INTO User_Settings VALUES ('Silver IMO',True,'20','amnra');
INSERT INTO User_Settings VALUES ('2 GOLDS IOI',FALSE ,'Programming','bahjatia');
INSERT INTO User_Settings VALUES ('From Shahrekord!',True,'Tigerous','AATeshnizi');
INSERT INTO User_Settings VALUES ('Bronze IMO ...',FALSE ,'zhzh','MhbdM');

INSERT INTO User_Session VALUES ('2011-01-10', 'LG G5', '2018-10-5', '192.168.1.1', 'Android', 'Sorooshbsl');
INSERT INTO User_Session VALUES ('1910-01-09', 'Oneplus 5T', '2018-10-6', '192.168.1.11', 'IOS', 'Ashkansoli');

INSERT INTO Group_Settings VALUES ('DB Of Rivadeh',FALSE,'mehran','rivadeh');
INSERT INTO Group_Settings VALUES ('DB Of Amini',TRUE,'morteza','amini');
INSERT INTO Group_Settings VALUES ('OS Of Kharrazi',FALSE,'mehdi','kharrazi');
INSERT INTO Group_Settings VALUES ('AI Of Rohban',TRUE,'mohammadhosein','rohban');
INSERT INTO Group_Settings VALUES ('DA Of Zarrabi',FALSE,'hamid','zarrabi');
INSERT INTO Group_Settings VALUES ('Madar Of Koohi',FALSE,'somayyeh','koohi');

INSERT INTO Channel_Settings VALUES ('Konkur Consulting',TRUE,'kooshaj','konkur');
INSERT INTO Channel_Settings VALUES ('Professional Emoji Analysis',TRUE,'mrkoosh','emoji');
INSERT INTO Channel_Settings VALUES ('Same Photo of the most Beautiful Face Ever!!!',TRUE,'lovelyaut','ostrich');
INSERT INTO Channel_Settings VALUES ('Sport of SUT News',TRUE,'Sharif','Sport');
INSERT INTO Channel_Settings VALUES ('Chelsea News for Iranian Fans',TRUE,'lampard','Chelsea');
INSERT INTO Channel_Settings VALUES ('Professional Analysis of Whether a man is an uncle or uncle?!!',TRUE,'uncle','daeiamoo');

INSERT INTO Message VALUES ('giiif', 5, 'id_j3', 'mrkooshaj');
INSERT INTO Channel_Messages VALUES ('emoji', 'id_j3', 0);
INSERT INTO Message VALUES ('giif', 5, 'id_j2', 'mrkooshaj');
INSERT INTO Channel_Messages VALUES ('emoji', 'id_j2', 0);
INSERT INTO Message VALUES ('gif', 5, 'id_j1', 'mrkooshaj');
INSERT INTO Channel_Messages VALUES ('emoji', 'id_j1', 0);
INSERT INTO Message VALUES ('giiiif', 5, 'id_j', 'mrkooshaj');
INSERT INTO Channel_Messages VALUES ('emoji', 'id_j', 0);
INSERT INTO Seen_Messages VALUES ('id_j', 'Sorooshbsl');
INSERT INTO Seen_Messages VALUES ('id_j1', 'Sorooshbsl');
INSERT INTO Seen_Messages VALUES ('id_j2', 'Sorooshbsl');
INSERT INTO Seen_Messages VALUES ('id_j3', 'Sorooshbsl');
INSERT INTO Message VALUES ('Moshavere', 45, 'id_i', 'mrkooshaj');
INSERT INTO Channel_Messages VALUES ('konkur', 'id_i', 0);
INSERT INTO Message VALUES ('amu ??', 35, 'id_k', 'mrkooshaj');
INSERT INTO Channel_Messages VALUES ('daeiamoo', 'id_k', 0);
INSERT INTO Message VALUES ('varzeshi', 15, 'id_l', 'mrkooshaj');
INSERT INTO Channel_Messages VALUES ('Sport', 'id_l', 0);
INSERT INTO Seen_Messages VALUES ('id_l', 'Sorooshbsl');

INSERT INTO Message VALUES ('menhaye_varzesh', 17, 'id_m', 'mrkooshaj');
INSERT INTO Channel_Messages VALUES ('Sport', 'id_m', 0);

INSERT INTO Blocked_User VALUES ('2018-11-11', 'Sorooshbsl', 'Ashkansoli');
INSERT INTO Blocked_User VALUES ('2018-11-11', 'mrkooshaj', 'Ashkansoli');
INSERT INTO Blocked_User VALUES ('2018-11-11', 'Sorooshbsl', 'mrkooshaj');

DELETE FROM Blocked_User WHERE Blocker_ID = 'Sorooshbsl';
DELETE FROM Blocked_User WHERE Blocked_ID = 'Ashkansoli';