#6
SELECT User.User_ID, User.User_Name, User.Phone_Number, User_Settings.Bio, User_Session.Last_Date
FROM User, User_Settings, User_Session
WHERE User.User_ID='Ashkansoli' and User.User_ID=User_Settings.User_ID and User.User_ID=User_Session.User_ID;