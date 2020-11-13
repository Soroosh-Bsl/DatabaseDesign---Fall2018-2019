import mysql.connector
import time as T
from elasticsearch import Elasticsearch
from time import gmtime, strftime
# import Time as Tim
import json

db = mysql.connector.connect(host='127.0.0.1', user='root', password='pass123', auth_plugin='mysql_native_password', database='db')
user = ""
cursor = db.cursor(buffered=True)

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
es.indices.delete(index='kaftar', ignore=[400, 404])
es.indices.delete(index='kaftar_member', ignore=[400, 404])

doc = {
        'sender': "SYS",
        'text': 'NONE',
        'time': 'NONE',
        'date': '1000-01-01',
        'receiver': 'NONE',
        'group': 'NONE',
        'channel': 'NONE'
      }
es.index(index="kaftar", doc_type='message', id=10, body=doc)



counter_message_id = 0


def name_by_user(username):

    if (username == "SYS"):
        return "System"

    elif (username == user):
        return "Me"

    else:
        query = "Select User_Name From USER Where Phone_Number = '" + username + "'"
        cursor.execute(query)
        result = cursor.fetchall()

        for x in result:
            if (x[0] == None):
                return '"' + username + '"'
            else:
                return '"' + x[0] + '"'
        return username

def name_by_user_join(username):
    query = "Select User_Name From USER Where Phone_Number = '" + username + "'"
    cursor.execute(query)
    result = cursor.fetchall()

    for x in result:
        if (x[0] == None):
            return username
        else:
            return x[0]


def printMessage(sender, text, time, date):
    if not sender:
        return
    for i in range(len(sender)):
        print("Sender:", name_by_user(sender[i]), " Time:\"", date[i], " ", time[i], "\"", " Message:\"", text[i], "\"", sep="")


def findGroupsAndChannels(es, user):
    try:
        res = es.search(index="kaftar_member", doc_type="membership", body={"query":{"match":{"member":str(user)}}})
    except Exception:
        return None, None, None
    groupsOfUser = []
    channelsOfUser = []
    res = res['hits']
    res = res['hits']
    for x in res:
        temp = x['_source']
        try:
            groupsOfUser.append(temp['group'])
        except KeyError:
            pass
        try:
            channelsOfUser.append(temp['channel'])
        except KeyError:
            pass
    return groupsOfUser, channelsOfUser, groupsOfUser+channelsOfUser


while True:
    T.sleep(1)
    query = "SELECT MAX(Message_ID) FROM Message"
    cursor.execute(query)
    result = cursor.fetchall()
    counter_message_id = int(result[0][0]) + 1 if result[0][0] is not None else 100000

    try:
        command = list(input().split())
    except EOFError:
        break
    # print(command)
    if command[0] == 'login':
        query = "SELECT DISTINCT Two_Step_Password, User.Phone_Number FROM User, User_Settings WHERE User.Phone_Number=User_Settings.User_Phone AND Phone_Number='" + command[1] + "'"
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result)==0:
            print("ID is not found.")
            continue
        for x in result:
            if x[0] is None:
                user = x[1]
                query = "UPDATE User_Session SET Last_Date=" + str( T.time()) + " WHERE USER_Phone='" + user + "'"
                cursor.execute(query)
            else:
                print("Enter your password:")
                password = input()
                if password == x[0]:
                    user = x[1]
                    query = "UPDATE User_Session SET Last_Date=" + str( T.time()) + " WHERE USER_Phone='" + user + "'"
                    cursor.execute(query)
                else:
                    user = ""
                    print("Access denied.")
        db.commit()
    elif command[0] == 'logout':
        if user == "":
            print("Access denied.")
            continue
        time_logout =  T.time()
        query = "UPDATE User_Session SET Last_Date=" + str(time_logout) + " WHERE USER_Phone='" + user + "'"
        cursor.execute(query)
        user = ""
        db.commit()
    elif command[0] == 'set_bio':
        if user == "":
            print("Access denied.")
            continue
        bio = command[1]
        for i in range(2, len(command)):
            bio += " " + command[i]
        query = "UPDATE User_Settings SET Bio='"+bio+"' WHERE USER_Phone= '"+user+"'"
        cursor.execute(query)
        db.commit()
    elif command[0] == 'send_message':
        message = command[2]
        for i in range(3, len(command)):
            message += " " + command[i]
        gm = gmtime()
        date = strftime("%Y-%m-%d", gm)
        time = strftime("%H:%M:%S", gm)
        query = "SELECT * FROM USER WHERE Phone_Number ='" + command[1] + "'"
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result) == 0:
            print("ID not found.")
        else:
            query = "SELECT * FROM USER WHERE Phone_Number ='" + user + "' AND Phone_Number NOT IN (SELECT Blocked_Number FROM Blocked_User WHERE Blocker_Number='" + \
                    command[1] + "')"
            cursor.execute(query)
            result = cursor.fetchall()
            if len(result) == 0:
                print("Access denied.")
            else:
                #ES:
                doc = {
                    'sender': str(user),
                    'text': message,
                    'time': str(time),
                    'date': str(date),
                    'receiver': str(command[1]),
                    'group': 'NONE',
                    'channel': 'NONE'
                }
                es.index(index="kaftar", doc_type='message', id=counter_message_id, body=doc)

                query = "INSERT INTO MESSAGE VALUES ('" + message + "', '" + str(time) + "', '" + str(
                    counter_message_id) + "', '" + user + "' , '" + str(date) + "')"
                cursor.execute(query)
                db.commit()
                query = "INSERT INTO Receiver_MESSAGE VALUES ('" + command[1] + "', '" + str(
                    counter_message_id) + "', False)"
                cursor.execute(query)
                db.commit()

                query = "SELECT Message_ID From Receiver_Message WHERE Receiver_Phone_Number = '" + user + "' AND Message_ID NOT IN (SELECT Message_ID From Seen_Messages Where User_Phone = '" + user + "')"
                cursor.execute(query)
                result = cursor.fetchall()

                for x in result:
                    query = "INSERT INTO Seen_Messages VALUES ('" + x[0] + "','" + user + "')"
                    cursor.execute(query)
                    db.commit()
                    query = "UPDATE Receiver_Message SET Seen = TRUE WHERE Message_ID = '" + x[0] + "'"
                    cursor.execute(query)
                    db.commit()


    elif command[0] == 'send_message_channel':
        query = "SELECT DISTINCT Creator_Phone FROM Channel_Settings WHERE Channel_ID='"+command[1]+"'"
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result) == 0:
            print("ID not found.")
        else:
            if result[0][0] != user:
                print("Access denied.")
            else:
                message = command[2]
                for i in range(3, len(command)):
                    message += " " + command[i]
                gm = gmtime()
                date = strftime("%Y-%m-%d", gm)
                time = strftime("%H:%M:%S", gm)
                query = "INSERT INTO MESSAGE VALUES ('" + message + "', '" + str(time) + "', '" + str(counter_message_id) + "', '" + user + "' , '" + str(date) + "')"
                cursor.execute(query)
                db.commit()
                query = "INSERT INTO Channel_Messages VALUES ('"+command[1]+"', '"+str(counter_message_id)+"', "+"0)"
                cursor.execute(query)
                db.commit()
                query = "INSERT INTO Seen_Messages VALUES ('"+str(counter_message_id)+"', '"+user+"')"
                cursor.execute(query)

                #ES:
                doc = {
                    'sender': str(user),
                    'text': message,
                    'time': str(time),
                    'date': str(date),
                    'receiver': 'NONE',
                    'group': 'NONE',
                    'channel': str(command[1])
                }
                es.index(index="kaftar", doc_type='message', id=counter_message_id, body=doc)

                db.commit()
    elif command[0] == 'send_message_group':
        query = "SELECT DISTINCT Member_Phone FROM Group_Enrollment WHERE GROUP_ID='"+command[1]+"'"
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result) == 0:
            print("ID not found.")
        else:
            query = "SELECT DISTINCT Member_Phone FROM Group_Enrollment WHERE GROUP_ID='"+command[1]+"' AND Member_Phone='"+user+"'"
            cursor.execute(query)
            result = cursor.fetchall()
            if len(result) == 0:
                print("Access denied.")
            else:
                message = command[2]
                for i in range(3, len(command)):
                    message += " " + command[i]
                gm = gmtime()
                date = strftime("%Y-%m-%d", gm)
                time = strftime("%H:%M:%S", gm)
                query = "INSERT INTO MESSAGE VALUES ('" + message + "', '" + str(time) + "', '" + str(counter_message_id) + "', '" + user + "' , '" + str(date) + "')"
                cursor.execute(query)
                db.commit()
                query = "INSERT INTO Group_Message VALUES ('"+command[1]+"', '"+str(counter_message_id)+"', "+"0)"
                cursor.execute(query)
                db.commit()
                query = "INSERT INTO Seen_Messages VALUES ('"+str(counter_message_id)+"', '"+user+"')"
                cursor.execute(query)

                #ES:
                doc = {
                    'sender': str(user),
                    'text': message,
                    'time': str(time),
                    'date': str(date),
                    'receiver': 'NONE',
                    'group': str(command[1]),
                    'channel': 'NONE'
                }
                es.index(index="kaftar", doc_type='message', id=counter_message_id, body=doc)

                db.commit()

                query = "SELECT Message_ID From Group_Message WHERE Group_ID = '" + command[1] + "' AND Message_ID NOT IN (SELECT Message_ID From Seen_Messages Where User_Phone = '" + user + "')"
                cursor.execute(query)
                result = cursor.fetchall()

                for x in result:
                    query = "INSERT INTO Seen_Messages VALUES ('" + x[0] + "','" + user + "')"
                    cursor.execute(query)
                    db.commit()

    elif command[0] == 'leave_channel':
        query = "DELETE FROM Channel_Members WHERE Channel_ID='"+command[1]+"' AND Member_Number='"+user+"'"
        cursor.execute(query)
        es.delete_by_query(index='kaftar_member', doc_type='membership', body={'query': {'bool': {'must': [{'match': {'member': str(user)}}, {'match': {'channel': str(command[1])}}]}}})
        db.commit()
    elif command[0] == 'leave_group':
        query = "DELETE FROM Group_Enrollment WHERE Group_ID='"+command[1]+"' AND Member_Phone='"+user+"'"
        cursor.execute(query)
        es.delete_by_query(index='kaftar_member', doc_type='membership', body={'query': {'bool': {'must': [{'match': {'member': str(user)}}, {'match': {'group': str(command[1])}}]}}})

        db.commit()

        query = "SELECT User_Name FROM User Where Phone_Number = '" + user + "'"
        cursor.execute(query)
        result = cursor.fetchall()

        gm = gmtime()
        date = strftime("%Y-%m-%d", gm)
        time = strftime("%H:%M:%S", gm)

        if result[0][0] is None:
            x = user
        else:
            x = result[0][0]

        query4 = "INSERT INTO Message Values ('" + str(x) + " left group','" + str(time) + "','" + str(
            counter_message_id) + "','SYS','" + str(date) + "')"
        cursor.execute(query4)

        query4 = "INSERT INTO Group_Message Values ('" + command[1] + "','" + str(counter_message_id) + "',0)"
        cursor.execute(query4)
        db.commit()

        doc = {
            'sender': "SYS",
            'text': str(name_by_user_join(user)) + " Left group",
            'time': str(time),
            'date': str(date),
            'receiver': 'NONE',
            'group': str(command[1]),
            'channel': 'NONE'
        }
        es.index(index="kaftar", doc_type='message', id=counter_message_id, body=doc)

    elif command[0] == 'home':
        if user == "":
            print("Access denied.")
            continue
        # z = "\'" + user + "\'"
        query = "SELECT Channel_Messages.Channel_ID AS ID, MAX(TIMESTAMP(Send_Date, Send_Time)) AS TIMING FROM Channel_Members, Channel_Messages, Message\n  \
WHERE Channel_Messages.Message_ID=Message.Message_ID AND Channel_Members.Member_Number='"+str(user)+"' \n  \
GROUP BY Channel_Messages.Channel_ID\n  \
UNION\n  \
SELECT Group_Enrollment.Group_ID AS ID, MAX(TIMESTAMP(Send_Date, Send_Time)) AS TIMING FROM Group_Enrollment, Group_Message, Message\n  \
WHERE Group_Message.Message_ID=Message.Message_ID AND Group_Enrollment.Member_Phone='"+user+"' \n  \
GROUP BY Group_Enrollment.Group_ID\n  \
UNION\n  \
    (SELECT ID, MAX(TIMING) FROM (SELECT Sender_Phone AS ID, MAX(TIMESTAMP(Send_Date, Send_Time)) AS TIMING FROM Receiver_Message, Message\n  \
WHERE Receiver_Message.Message_ID=Message.Message_ID AND Receiver_Message.Receiver_Phone_Number='"+user+"' \n  \
GROUP BY Sender_Phone\n  \
UNION\n  \
SELECT Receiver_Phone_Number AS ID, MAX(TIMESTAMP(Send_Date, Send_Time)) AS TIMING FROM Receiver_Message, Message\n  \
WHERE Receiver_Message.Message_ID=Message.Message_ID AND Sender_Phone='"+user+"' \n  \
GROUP BY ID) AS TEMP\n  \
GROUP BY ID) ORDER BY TIMING DESC LIMIT 8"
        cursor.execute(query)
        result = cursor.fetchall()
        query = "SELECT Phone_Number FROM User"
        cursor.execute(query)
        users = cursor.fetchall()
        all_users = []
        for i in range(len(users)):
            all_users.append(users[i][0])
        query = "SELECT Channel_ID FROM Channel"
        cursor.execute(query)
        channels = cursor.fetchall()
        all_channels = []
        for i in range(len(channels)):
            all_channels.append(channels[i][0])
        # channels = channels[:][0] if len(channels) != 0 else []
        query = "SELECT Group_ID FROM MGroup"
        cursor.execute(query)
        groups = cursor.fetchall()
        all_groups = []
        for i in range(len(groups)):
            all_groups.append(groups[i][0])
        # groups = groups[:][0] if len(groups) != 0 else []
        for i in range(len(result)):
            if result[i][0] in all_users:
                query = "SELECT COUNT(*) FROM Message, Receiver_Message WHERE Message.Message_ID=Receiver_Message.Message_ID AND Message.Sender_Phone='" + result[i][0] + "' AND Receiver_Message.Receiver_Phone_Number ='"+user+"' AND Receiver_Message.SEEN=FALSE"
                cursor.execute(query)
                unread = cursor.fetchall()
                unread = unread[0][0]
                query = "SELECT User_Name FROM User WHERE Phone_Number='"+result[i][0]+"'"
                cursor.execute(query)
                audience = cursor.fetchall()
                audience = audience[0][0] if len(audience) != 0 else None
                audience = audience if audience != None else result[i][0]
                print("chat with "+str(audience)+", unread_count="+str(unread))
            elif result[i][0] in all_groups:
                query = "SELECT COUNT(*) FROM Group_Message WHERE Group_ID='"+result[i][0]+"' AND Message_ID NOT IN (SELECT Message_ID FROM Seen_messages WHERE User_Phone='"+user+"')"
                cursor.execute(query)
                unread = cursor.fetchall()
                unread = unread[0][0]
                query = "SELECT Group_Name FROM MGroup WHERE Group_ID='" + result[i][0] + "'"
                cursor.execute(query)
                audience = cursor.fetchall()
                audience = audience[0][0] if len(audience) != 0 else None
                audience = audience if audience != None else result[i][0]
                print("group "+str(audience)+", unread_count="+str(unread))
            elif result[i][0] in all_channels:
                query = "SELECT COUNT(*) FROM Channel_Messages WHERE Channel_ID='" +result[i][0]+"' AND Message_ID NOT IN (SELECT Message_ID FROM Seen_messages WHERE User_Phone='"+user+"')"
                cursor.execute(query)
                unread = cursor.fetchall()
                unread = unread[0][0]
                query = "SELECT Channel_Name FROM Channel WHERE Channel_ID='" + result[i][0] + "'"
                cursor.execute(query)
                audience = cursor.fetchall()
                audience = audience[0][0] if len(audience) != 0 else None
                audience = audience if audience != None else result[i][0]
                print("channel "+str(audience)+", unread_count="+str(unread))

        db.commit()

#KOOOOOOOOSHAAAAAAAAAAAAAAAA
    elif command[0] == 'unblock_user':
        query1 = "Select * From Blocked_User Where Blocker_Number = '" + user + "'And Blocked_Number = '" +    \
            command[1] + "'"

        cursor.execute(query1)
        result = cursor.fetchall()

        if len(result) == 0:
            print("ID is not found.")

        else:
            query = "DELETE FROM Blocked_User WHERE Blocker_Number = '" +  \
                    user + "'And Blocked_Number = '" +  \
                    command[1] + "'"

            cursor.execute(query)
        db.commit()
    elif command[0] == 'create_user':

        query1 = "Select * FROM User Where Phone_Number = '" + command[1] + "'"

        cursor.execute(query1)
        result = cursor.fetchall()

        if len(result) == 0:
            query = "INSERT INTO User Values (NULL,NULL,'" + \
                    command[1] + "')"

            cursor.execute(query)

            query = "INSERT INTO User_Settings Values (NULL,NULL,NULL,'" + \
                    command[1] + "')"

            cursor.execute(query)

            gm = gmtime()
            date = strftime("%Y-%m-%d", gm)

            query = "INSERT INTO User_Session Values('" + str(date) + "' ,NULL, " + str( T.time()) + " ,NULL,NULL, '" + command[1] + "')"

            cursor.execute(query)

        else:
            print("Access denied.")
        db.commit()
    elif command[0] == 'set_name':
        query = "UPDATE User SET User_Name = '" +  \
            command[1] + "' WHERE Phone_Number ='" +  \
            user + "'"

        cursor.execute(query)
        db.commit()
    elif command[0] == 'set_channel_link':
        query = "Update Channel SET Channel_Link = '" +  \
            command[2] + "'Where Channel_ID = '" +  \
            command[1] + "'"

        query1 = "Select Creator_Phone FROM Channel_Settings WHERE Channel_ID = '" +  \
                 command[1] + "'AND Creator_Phone ='" + user + "'"

        cursor.execute(query1)
        result = cursor.fetchall()

        if len(result) == 0:
            print("Access denied.")

        else:
            cursor.execute(query)
        db.commit()
    elif command[0] == 'set_group_link':
        query = "Update MGroup SET Group_Link = '" +  \
                command[2] + "'Where Group_ID ='" +  \
                command[1] + "'"

        query1 = "Select Creator_Phone FROM Group_Settings WHERE Group_ID ='" +  \
                 command[1] + "'AND Creator_Phone ='" + user + "'"

        cursor.execute(query1)
        result = cursor.fetchall()

        if len(result) == 0:
            print("Access denied.")

        else:
            cursor.execute(query)
        db.commit()
    elif command[0] == 'join_channel':
        if(user == ""):
            print("ID is not found.")
            continue
        query = "INSERT INTO Channel_Members VALUES ('" +  \
            user + "','" +  \
            command[1] + "')"

        query1 = "SELECT Channel_ID FROM Channel Where Channel_ID ='" +  \
            command[1] + "'"

        cursor.execute(query1)
        result = cursor.fetchall()

        if len(result) == 0:
            print("ID is not found.")

        else:
            es.index(index='kaftar_member', doc_type='membership', body={'member': str(user), 'channel': str(command[1])})

            cursor.execute(query)
        db.commit()

    elif command[0] == 'join_link':
        if(user == ""):
            print("ID is not found.")
            continue
        query1 = "SELECT Channel_ID FROM Channel WHERE Channel_Link ='" +  \
            command[1] + "'"

        query2 = "Select Group_ID FROM MGroup Where Group_Link ='" +  \
            command[1] + "'"

        cursor.execute(query1)
        channel_id = cursor.fetchall()

        cursor.execute(query2)
        group_id = cursor.fetchall()

        query = "SELECT User_Name FROM User Where Phone_Number = '" + user + "'"
        cursor.execute(query)
        result = cursor.fetchall()

        for x in channel_id:
            query3 = "INSERT INTO Channel_Members Values ('" + \
                     user + "','" + \
                     x[0] + "')"
            es.index(index='kaftar_member', doc_type='membership', body={'member': str(user), 'channel': str(x[0])})
            cursor.execute(query3)
            db.commit()

        for y in group_id:
            query4 = "INSERT INTO Group_Enrollment Values ('" + \
                     user + "','" + \
                     y[0] + "')"
            es.index(index='kaftar_member', doc_type='membership', body={'member': str(user), 'group': str(y[0])})

            cursor.execute(query4)
            db.commit()

            gm = gmtime()
            date = strftime("%Y-%m-%d", gm)
            time = strftime("%H:%M:%S", gm)

            if (result[0][0] == None):
                tquery = user
            else:
                tquery = result[0][0]

            query4 = "INSERT INTO Message Values ('" + tquery + " joined group','" + str(time) + "','" + str(counter_message_id) + "','SYS','" + str(date) + "')"

            cursor.execute(query4)
            db.commit()

            query4 = "INSERT INTO Group_Message Values ('" + y[0] + "','" + str(counter_message_id) + "',1)"
            cursor.execute(query4)
            db.commit()

            query4 = "INSERT INTO Seen_Messages Values ('" + str(counter_message_id) + "','" + user + "')"
            cursor.execute(query4)
            db.commit()

            doc = {
                'sender': "SYS",
                'text': str(name_by_user_join(user)) + " Joined group",
                'time': str(time),
                'date': str(date),
                'receiver': 'NONE',
                'group': str(y[0]),
                'channel': 'NONE'
            }
            es.index(index="kaftar", doc_type='message', id=counter_message_id, body=doc)

        if len(channel_id) == 0 and len(group_id) == 0:
            print("ID is not found.")

        # elif len(group_id) == 0:
        #     cursor.execute(query3)
        # elif len(channel_id) == 0:
        #     cursor.execute(query4)
        db.commit()

    elif command[0] == 'view_user_profile':
        query = "Select User_Name,Bio FROM User,User_Settings Where User_Phone = Phone_Number And Phone_Number = '" + \
                command[1] + "'"
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result) == 0:
            print("ID is not found.")
        else:
            for x in result:
                if (x[0] == None):
                    print("Name:NULL", end=" ")
                else:
                    print('Name:'+ '\"' + x[0] + '\"', end=" ")
                if (x[1] == None):
                    print("Bio:NULL")
                else:
                    print('Bio:'+'\"'+ x[1]+ '\"')
        db.commit()

    elif command[0] == 'view_channel_profile':

        query = "SELECT Channel_Name, Channel_Link FROM Channel,Channel_Settings WHERE Channel.Channel_ID = "  \
                "Channel_Settings.Channel_ID AND Channel.Channel_ID ='" +  \
        command[1] + "'"

        cursor.execute(query)
        result = cursor.fetchall()

        query2 = "SELECT * FROM Channel_Members WHERE Channel_ID = '" + command[1] + "' AND Member_Number = '" + user + "'"
        cursor.execute(query2)
        res = cursor.fetchall()

        if len(result) == 0:
            print("ID is not found.")

        elif len(res) == 0:
            print("Access denied.")

        else:

            query3 = "SELECT COUNT(Member_Number) FROM Channel_Members GROUP BY Channel_ID HAVING Channel_ID = '" + command[1] + "'"

            cursor.execute(query3)
            mem_count = cursor.fetchall()

            for x in result:
                print('Name:'+ '\"'+ x[0]+ '\"'+ ' MembersCount:'+ str(mem_count[0][0])+ ' Link:' + '\"' +x[1] + '\"',end = " ")
                query1 = query = "SELECT User_Name,Phone_Number FROM User, Channel_Members,User_Session WHERE Member_Number = Phone_Number AND "  \
                    "Channel_ID ='" + command[1] + "' And Member_Number = User_Phone Order By Last_Date DESC"

                cursor.execute(query1)
                result = cursor.fetchall()

                query2 = "Select Creator_Phone FROM Channel_Settings WHERE Channel_ID ='" +  \
                         command[1] + "'AND Creator_Phone ='" + user + "'"

                cursor.execute(query2)
                is_admin = cursor.fetchall()

                if len(is_admin) > 0:
                    print('Creator:' + '\"' + name_by_user_join(user) + '\"',end = " ")
                    print("Members:",end = "")
                    for x in result:
                        if (x == result[0]):
                            if (x[0] != None):
                                print('\"' + x[0] + '\"' + ' ', end="")
                            else:
                                print('\"' + x[1] + '\"' + ' ', end="")
                        else:
                            if (x[0] != None):
                                print(',' + '\"' + x[0] + '\"' + ' ', end="")
                            else:
                                print(',' + '\"' + x[1] + '\"' + ' ', end="")

                    print()

                else:
                    print()

        db.commit()

    elif command[0] == 'view_group_profile':
        query = "SELECT Group_Name,Group_Link,Creator_Phone FROM MGroup,Group_Settings WHERE MGroup.Group_ID ="  \
                "Group_Settings.Group_ID AND MGroup.Group_ID ='" +  \
                command[1] + "'"

        cursor.execute(query)
        result = cursor.fetchall()

        if len(result) == 0:
            print("ID is not found.")

        else:

            query1 = query = "SELECT * FROM Group_Enrollment Where Member_Phone = '" + user + "' AND Group_ID IN ("  \
                "Select Group_ID FROM MGroup WHERE Group_ID = '" + command[1] + "');"

            cursor.execute(query1)
            res = cursor.fetchall()

            query3 = "SELECT COUNT(Member_Phone) FROM Group_Enrollment GROUP BY Group_ID HAVING Group_ID = '" +  \
                     command[1] + "'"

            cursor.execute(query3)
            mem_count = cursor.fetchall()

            if len(res) == 0:
                print("Access denied.")

            else:
                for x in result:

                    print('Name:' + '\"' + x[0] + '\"' + ' MembersCount:' + str(mem_count[0][0]) + ' Link:' + '\"' + x[1] + '\"' + ' Creator:' + '\"' + name_by_user_join(x[2]) + '\"', end = " ")

                    query1 = "SELECT User_Name,Phone_Number FROM User, Group_Enrollment,User_Session WHERE Member_Phone = Phone_Number AND "  \
                             "Group_ID ='" + command[1] + "' And User_Phone = Phone_Number ORDER BY Last_Date DESC"

                    cursor.execute(query1)
                    result = cursor.fetchall()

                    print("Members:",end="")
                    for x in result:
                        if (x == result[0]):
                            if (x[0] != None):
                                print('\"' + x[0] + '\"' + ' ', end="")
                            else:
                                print('\"' + x[1] + '\"' + ' ', end="")
                        else:
                            if (x[0] != None):
                                print(',' + '\"' + x[0] + '\"' + ' ', end="")
                            else:
                                print(',' + '\"' + x[1] + '\"' + ' ', end="")

                    print()
        db.commit()
    elif command[0] == 'view_chat':
        query = "SELECT COUNT(*) FROM Message JOIN Receiver_Message ON Message.Message_ID = " \
                "Receiver_Message.Message_ID WHERE (Sender_Phone = \'" + command[
                    1] + "\' AND Receiver_Phone_Number = \'" + user + "\' AND Seen = FALSE);"
        cursor.execute(query)
        unreadNum = str(cursor.fetchone()[0])
        query = "SELECT User_Name, Phone_Number FROM User WHERE Phone_Number = \'" + command[1] + "\';"
        cursor.execute(query)
        if cursor.rowcount <= 0:
            print("ID is not found.")
            continue
        audience = cursor.fetchone()[0]
        audience = str(audience) if audience is not None else command[1]
        #print("chat with " + audience + ", unread_count = " + unreadNum)
        query = "SELECT Text, Send_Time, Sender_Phone,Send_Date FROM Message JOIN Receiver_Message ON Message.Message_ID = " \
                "Receiver_Message.Message_ID WHERE (Sender_Phone = \'" + command[
                    1] + "\' AND Receiver_Phone_Number = \'" + user + "\') OR (" \
                + "Sender_Phone = \'" + user + "\' AND Receiver_Phone_Number = \'" + command[
                    1] + "\') ORDER BY Send_Time ASC" \
                + " LIMIT 20;"
        cursor.execute(query)
        result = cursor.fetchall()
        for x in result:
            print('Sender:' + str("Me" if x[2] == user else '\"' + audience + '\"') + ' Time:' + '\"' + str(x[3]) + ' ' + str(x[1]) + '\"' + ' Message:' + '\"' + str(x[0] + '\"'))
        query = "UPDATE Receiver_Message JOIN Message ON Message.Message_ID = " \
                "Receiver_Message.Message_ID SET Seen = TRUE WHERE (Sender_Phone = \'" + command[
                    1] + "\' AND Receiver_Phone_Number = \'" + user + "\');"
        cursor.execute(query)
        db.commit()

    elif command[0] == 'view_channel':
        query = "SELECT Member_Number FROM Channel_Members WHERE (Member_Number = \'" + user + "\' AND Channel_ID = \'" + \
                command[1] + "\');"
        cursor.execute(query)
        if len(cursor.fetchall()) <= 0:
            print("Access denied.")
            continue
        query = "SELECT Message.Message_ID FROM Message JOIN Channel_Messages ON Message.Message_ID = Channel_Messages.Message_ID " \
                "WHERE Channel_ID = \'" + command[1] + "\' AND Message.Message_ID not in (\
                                  SELECT Seen_Messages.Message_ID\
                                  FROM Seen_Messages\
                                  WHERE Seen_Messages.User_Phone = \'" + user + "\'" \
                + ");"
        cursor.execute(query)
        unreadMessages = cursor.fetchall()
        unreadNum = str(cursor.rowcount)
        query = 'SELECT Channel_Name FROM Channel WHERE Channel_ID = ' + command[1] + ';'
        cursor.execute(query)
        if cursor.rowcount <= 0:
            print("ID is not found.")
            continue
        groupName = str(cursor.fetchone()[0])
        #print("channel " + groupName + ", unread_count = " + unreadNum)
        for x in unreadMessages:
            query = "INSERT INTO Seen_Messages VALUE (\'" + str(x[0]) + "\', \'" + user + "\');"
            cursor.execute(query)
            db.commit()
        query = "SELECT Text, Send_Time, Sender_Phone, User_Name,Send_Date FROM Message JOIN Channel_Messages ON Message.Message_ID = " \
                "Channel_Messages.Message_ID JOIN User ON Phone_Number = Sender_Phone WHERE (Channel_ID = \'" + command[
                    1] + \
                "\') ORDER BY Send_Time ASC LIMIT 20"
        cursor.execute(query)
        result = cursor.fetchall()
        for x in result:
            print('Sender:' + str("Me" if x[2] == user else ('\"' + x[2] + '\"' if x[3] is None else ('\"' + x[3] + '\"' if x[3] != "System" else x[3]))) + ' Time:' + '\"' + str(x[4]) + ' ' + str(x[1]) + '\"' + ' Message:\"' + str( \
                x[0]) + "\"")


    elif command[0] == 'view_group':
        query = "SELECT Member_Phone FROM Group_Enrollment WHERE (Member_Phone = \'" + user + "\' AND Group_ID = \'" + \
                command[1] + "\');"
        cursor.execute(query)
        if len(cursor.fetchall()) <= 0:
            print("Access denied.")
            continue
        query = "SELECT Message.Message_ID FROM Message JOIN Group_Message ON Message.Message_ID = Group_Message.Message_ID "\
                "WHERE Group_ID = \'" + command[1] + "\' AND Message.Message_ID not in (\
                      SELECT Seen_Messages.Message_ID\
                      FROM Seen_Messages\
                      WHERE Seen_Messages.User_Phone = \'" + user + "\'"\
                      + ");"
        cursor.execute(query)
        unreadMessages = cursor.fetchall()
        unreadNum = str(cursor.rowcount)
        query = 'SELECT Group_Name FROM MGroup WHERE Group_ID = ' + command[1] + ';'
        cursor.execute(query)
        if cursor.rowcount <= 0:
            print("ID is not found.")
            continue
        groupName = str(cursor.fetchone()[0])
        #print("group " + groupName + ", unread_count = " + unreadNum)
        for x in unreadMessages:
            query = "INSERT INTO Seen_Messages VALUE (\'" + str(x[0]) + "\', \'" + user + "\');"
            cursor.execute(query)
            db.commit()
        query = "SELECT Text, Send_Time, Sender_Phone, User_Name,Send_Date FROM Message JOIN Group_Message ON Message.Message_ID = " \
                "Group_Message.Message_ID JOIN User ON Phone_Number = Sender_Phone WHERE (Group_ID = \'" + command[1] + \
                "\') ORDER BY Send_Time ASC LIMIT 20"
        cursor.execute(query)
        result = cursor.fetchall()
        for x in result:
            print('Sender:' + str("Me" if x[2] == user else ('\"' + x[2] + '\"' if x[3] is None else ('\"' + x[3] + '\"' if x[3] != "System" else x[3]) )) + ' Time:' + '\"' + str(x[4]) + ' ' + str(x[1]) + '\"' + ' Message:\"' + str(x[0]) + "\"")
    elif command[0] == 'set_self_destruct':
        selfDestructionTime = 0
        if command[1] == '0':
            selfDestructionTime = 0
        elif command[1] == '1':
            selfDestructionTime = 30
        elif command[1] == '2':
            selfDestructionTime = 90
        elif command[1] == '3':
            selfDestructionTime = 180
        query = "UPDATE User_Settings SET Self_Destruct = " + str(selfDestructionTime) + \
                " WHERE User_Phone = \'" + user + "\';"

        cursor.execute(query)
        db.commit()

    elif command[0] == 'set_password':
        if user == "":
            print("Access denied.")
            continue
        query = "UPDATE User_Settings SET Two_Step_Password = \'" + str(command[1]) + \
                "\' WHERE User_Phone = \'" + user + "\';"
        cursor.execute(query)
        db.commit()

    elif command[0] == 'block_user':
        if user == "":
            print("Access denied.")
            continue
        query = "Select * FROM User Where Phone_Number = '" + command[1] + "'"
        cursor.execute(query)
        res = cursor.fetchall()
        if len(res) == 0:
            print("ID is not found.")
        else:
            gm = gmtime()
            date = strftime("%Y-%m-%d", gm)
            query = "INSERT INTO Blocked_User VALUES (\'" + date + "\',\'" + user + "\',\'" + command[1] + "\');"
            cursor.execute(query)
            db.commit()


    elif command[0] == 'create_channel':
        if user == "":
            print("Access denied.")
            continue
        query = "SELECT Channel_ID FROM Channel WHERE Channel_ID = \'" + command[1] + "\';"
        cursor.execute(query)
        if cursor.rowcount > 0:
            print("Access denied.")
            continue
        query = "INSERT INTO Channel VALUES (\'" + command[1] + "\', NULL, \'" + command[2] + "\', NULL);"
        cursor.execute(query)
        db.commit()
        query = "INSERT INTO Channel_Settings VALUES (NULL, 0, NULL, \'" + command[1] + "\', \'" + user + "\');"
        cursor.execute(query)
        db.commit()
        query = "INSERT INTO Channel_Members VALUES ('" + user + "','" + command[1] + "')"
        cursor.execute(query)
        db.commit()

        es.index(index='kaftar_member', doc_type='membership', body={'member': str(user), 'channel': str(command[1])})

        gm = gmtime()
        date = strftime("%Y-%m-%d", gm)
        time = strftime("%H:%M:%S", gm)

        query = "INSERT INTO Message VALUES ('channel created','" + str(time) + "','" + str(
            counter_message_id) + "','SYS','" + date + "')"
        cursor.execute(query)
        db.commit()

        query = "INSERT INTO Channel_Messages Values ('" + command[1] + "','" + str(counter_message_id) + "',1)"
        cursor.execute(query)
        db.commit()

        query = "INSERT INTO Seen_Messages Values ('" + str(counter_message_id) + "','" + user + "')"
        cursor.execute(query)
        db.commit()

        doc = {
            'sender': "SYS",
            'text': "Channel Created",
            'time': str(time),
            'date': str(date),
            'receiver': 'NONE',
            'group': 'NONE',
            'channel': str(command[1])
        }
        es.index(index="kaftar", doc_type='message', id=counter_message_id, body=doc)

    elif command[0] == 'create_group':
        if user == "":
            print("Access denied.")
            continue
        query = "SELECT Group_ID FROM MGroup WHERE Group_ID = \'" + command[1] + "\';"
        cursor.execute(query)
        if cursor.rowcount > 0:
            print("Access denied.")
            continue
        query = "INSERT INTO MGroup VALUES (\'" + command[1] + "\', NULL, \'" + command[2] + "\', NULL);"
        cursor.execute(query)
        db.commit()
        query = "INSERT INTO Group_Settings VALUES (NULL, 0, NULL,\'" + command[1] + "\', \'" + user + "\');"
        cursor.execute(query)
        db.commit()
        query = "INSERT INTO Group_Enrollment VALUES ('" + user + "','" + command[1] + "')"
        cursor.execute(query)
        db.commit()

        es.index(index='kaftar_member', doc_type='membership', body={'member': str(user), 'group': str(command[1])})

        gm = gmtime()
        date = strftime("%Y-%m-%d", gm)
        time = strftime("%H:%M:%S", gm)

        query = "INSERT INTO Message VALUES ('group created','" + str(time) + "','" + str(counter_message_id) + "','SYS','" + date + "')"
        cursor.execute(query)
        db.commit()

        query = "INSERT INTO Group_Message Values ('" + command[1] + "','" + str(counter_message_id) + "',1)"
        cursor.execute(query)
        db.commit()
        doc = {
            'sender': "SYS",
            'text': "Group Created",
            'time': str(time),
            'date': str(date),
            'receiver': 'NONE' ,
            'group': str(command[1]),
            'channel': 'NONE'
        }
        es.index(index="kaftar", doc_type='message', id=counter_message_id, body=doc)

        query = "INSERT INTO Seen_Messages Values ('" + str(counter_message_id) + "','" + user + "')"
        cursor.execute(query)
        db.commit()

    elif command[0] == 'set_channel_link':
        if user == "":
            print("Access denied.")
            continue
        query = 'SELECT Channel_Name FROM Channel WHERE Channel_ID = ' + command[1] + ';'
        cursor.execute(query)
        if cursor.rowcount <= 0:
            print("ID is not found.")
            continue
        query = "SELECT Creator_Phone FROM Channel_Settings WHERE Channel_ID = \'" + command[1] + "\';"
        cursor.execute()
        creator = str(cursor.fetchone()[0])
        if creator != user:
            print("Access denied.")
            continue
        query = "UPDATE Channel SET Channel_Link = \'" + command[2] + "\' WHERE Channel_ID = \'" + command[1] + "\';"
        cursor.execute(query)
        db.commit()


#28
    elif command[0] == "count_unread":
        query = "SELECT Channel_Messages.Channel_ID AS ID, MAX(TIMESTAMP(Send_Date, Send_Time)) AS TIMING FROM Channel_Members, Channel_Messages, Message\n  \
        WHERE Channel_Messages.Message_ID=Message.Message_ID AND Channel_Members.Member_Number='" + str(user) + "' \n  \
        GROUP BY Channel_Members.Channel_ID\n  \
        UNION\n  \
        SELECT Group_Enrollment.Group_ID AS ID, MAX(TIMESTAMP(Send_Date, Send_Time)) AS TIMING FROM Group_Enrollment, Group_Message, Message\n  \
        WHERE Group_Message.Message_ID=Message.Message_ID AND Group_Enrollment.Member_Phone='" + user + "' \n  \
        GROUP BY Group_Enrollment.Group_ID\n  \
        UNION\n  \
            (SELECT ID, MAX(TIMING) FROM (SELECT Sender_Phone AS ID, MAX(TIMESTAMP(Send_Date, Send_Time)) AS TIMING FROM Receiver_Message, Message\n  \
        WHERE Receiver_Message.Message_ID=Message.Message_ID AND Receiver_Message.Receiver_Phone_Number='" + user + "' \n  \
        GROUP BY Sender_Phone\n  \
        UNION\n  \
        SELECT Receiver_Phone_Number AS ID, MAX(TIMESTAMP(Send_Date, Send_Time)) AS TIMING FROM Receiver_Message, Message\n  \
        WHERE Receiver_Message.Message_ID=Message.Message_ID AND Sender_Phone='" + user + "' \n  \
        GROUP BY ID) AS TEMP\n  \
        GROUP BY ID) ORDER BY TIMING DESC"
        cursor.execute(query)
        result = cursor.fetchall()
        query = "SELECT Phone_Number FROM User"
        cursor.execute(query)
        users = cursor.fetchall()
        all_users = []
        for i in range(len(users)):
            all_users.append(users[i][0])
        query = "SELECT Channel_ID FROM Channel"
        cursor.execute(query)
        channels = cursor.fetchall()
        all_channels = []
        for i in range(len(channels)):
            all_channels.append(channels[i][0])
        # channels = channels[:][0] if len(channels) != 0 else []
        query = "SELECT Group_ID FROM MGroup"
        cursor.execute(query)
        groups = cursor.fetchall()
        all_groups = []
        for i in range(len(groups)):
            all_groups.append(groups[i][0])
        # groups = groups[:][0] if len(groups) != 0 else []
        total_unread = 0
        for i in range(len(result)):
            if result[i][0] in all_users:
                query = "SELECT COUNT(*) FROM Message, Receiver_Message WHERE Message.Message_ID=Receiver_Message.Message_ID AND Message.Sender_Phone='" + \
                        result[i][
                            0] + "' AND Receiver_Message.Receiver_Phone_Number ='" + user + "' AND Receiver_Message.SEEN=FALSE"
                cursor.execute(query)
                unread = cursor.fetchall()
                unread = unread[0][0]
                total_unread += unread
            elif result[i][0] in all_groups:
                query = "SELECT COUNT(*) FROM Group_Message WHERE Group_ID='" + result[i][
                    0] + "' AND Message_ID NOT IN (SELECT Message_ID FROM Seen_messages WHERE User_Phone='" + user + "')"
                cursor.execute(query)
                unread = cursor.fetchall()
                unread = unread[0][0]
                total_unread += unread
            elif result[i][0] in all_channels:
                query = "SELECT COUNT(*) FROM Channel_Messages WHERE Channel_ID='" + result[i][
                    0] + "' AND Message_ID NOT IN (SELECT Message_ID FROM Seen_messages WHERE User_Phone='" + user + "')"
                cursor.execute(query)
                unread = cursor.fetchall()
                unread = unread[0][0]
                total_unread += unread
        print(total_unread)

    elif command[0] == "search_all":
        all_groups, all_channels, all = findGroupsAndChannels(es, user)
        if all_channels and all_groups:
            doc = {"size": 1000,
                "query": {
                    "bool": {
                        "must": [
                            {"bool": {"should": [{"bool": {"must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}},{"match": {"channel": "NONE"}}]}}] +
                                                [{"bool": {
                                                    "must": [{"match": {"receiver": str(user)}}, {"match": {"group": "NONE"}},
                                                             {"match": {"channel": "NONE"}}]}}] +
                                       [{"match": {"group": x}} for x in all_groups] +
                                    [{"match": {"channel": x}} for x in all_channels]}},
                            {"bool": {"must": [{"match": {"text": command[i]}} for i in range(1, len(command))]}}
                        ]
                    }
                }
            }
        elif all_groups:
            doc = {"size": 1000,
                "query": {
                    "bool": {
                        "must": [
                            {"bool": {"should": [{"bool": {
                                "must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}},
                                         {"match": {"channel": "NONE"}}]}}] +
                                                [{"bool": {
                                                    "must": [{"match": {"receiver": str(user)}},
                                                             {"match": {"group": "NONE"}},
                                                             {"match": {"channel": "NONE"}}]}}] +
                                                [{"match": {"group": x}} for x in all_groups]}},
                            {"bool": {"must": [{"match": {"text": command[i]}} for i in range(1, len(command))]}}
                        ]
                    }
                }
            }
        elif all_channels:
            doc = {"size": 1000,
                "query": {
                    "bool": {
                        "must": [
                            {"bool": {"should": [{"bool": {
                                "must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}},
                                         {"match": {"channel": "NONE"}}]}}] +
                                                [{"bool": {
                                                    "must": [{"match": {"receiver": str(user)}},
                                                             {"match": {"group": "NONE"}},
                                                             {"match": {"channel": "NONE"}}]}}] +
                                                [{"match": {"channel": x}} for x in all_channels]}},
                            {"bool": {"must": [{"match": {"text": command[i]}} for i in range(1, len(command))]}}
                        ]
                    }
                }
            }
        else:
            doc = { "size": 1000,
                "query": {
                    "bool": {
                        "must": [
                            {"bool": {"should": [{"bool": {
                                "must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}},
                                         {"match": {"channel": "NONE"}}]}}] +
                                                [{"bool": {
                                                    "must": [{"match": {"receiver": str(user)}},
                                                             {"match": {"group": "NONE"}},
                                                             {"match": {"channel": "NONE"}}]}}]}},
                            {"bool": {"must": [{"match": {"text": command[i]}} for i in range(1, len(command))]}}
                        ]
                    }
                }
            }
        res = es.search(index="kaftar", doc_type="message", body=doc)
        try:
            res = res['hits']
            res = res['hits']
            sender = []
            time = []
            date = []
            textOfMessage = []
            for x in res:
                temp = x['_source']
                try:
                    sender.append(temp['sender'])
                    time.append(temp['time'])
                    date.append(temp['date'])
                    textOfMessage.append(temp['text'])
                except KeyError:
                    pass
            printMessage(sender, textOfMessage, time, date)
        except KeyError:
            pass
    elif command[0] == "search_chat":
        doc = {"size": 1000,
               "query": {
                   "bool": {
                       "must": [
                           {"bool": {"should": [{"bool": {
                               "must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}}, {"match": {"receiver": str(command[1])}},
                                        {"match": {"channel": "NONE"}}]}}] +
                                               [{"bool": {
                                                   "must": [{"match": {"receiver": str(user)}}, {"match":{"sender": str(command[1])}},
                                                            {"match": {"group": "NONE"}},
                                                            {"match": {"channel": "NONE"}}]}}]}},
                           {"bool": {"must": [{"match": {"text": command[i]}} for i in range(2, len(command))]}}
                       ]
                   }
               }
               }
        res = es.search(index="kaftar", doc_type="message", body=doc)
        try:
            res = res['hits']
            res = res['hits']
            sender = []
            time = []
            date = []
            textOfMessage = []
            for x in res:
                temp = x['_source']
                try:
                    sender.append(temp['sender'])
                    time.append(temp['time'])
                    date.append(temp['date'])
                    textOfMessage.append(temp['text'])
                except KeyError:
                    pass
            printMessage(sender, textOfMessage, time, date)
        except KeyError:
            pass
    elif command[0] == "search_group":
        all_groups, _, __ = findGroupsAndChannels(es, user)
        if command[1] not in all_groups:
            print("Access denied.")
            continue
        doc = {"size": 1000,
               "query": {
                   "bool": {
                       "must": [
                           {"bool": {"must": {"match": {"group": str(command[1])}}}},
                           {"bool": {"must": [{"match": {"text": command[i]}} for i in range(2, len(command))]}}
                       ]
                   }
               }
               }
        res = es.search(index="kaftar", doc_type="message", body=doc)
        try:
            res = res['hits']
            res = res['hits']
            sender = []
            time = []
            date = []
            textOfMessage = []
            for x in res:
                temp = x['_source']
                try:
                    sender.append(temp['sender'])
                    time.append(temp['time'])
                    date.append(temp['date'])
                    textOfMessage.append(temp['text'])
                except KeyError:
                    pass
            printMessage(sender, textOfMessage, time, date)
        except KeyError:
            pass
    elif command[0] == "search_channel":
        _, all_channels, __ = findGroupsAndChannels(es, user)
        if command[1] not in all_channels:
            print("Access denied.")
            continue
        doc = {"size": 1000,
               "query": {
                   "bool": {
                       "must": [
                           {"bool": {"must": {"match": {"channel": str(command[1])}}}},
                           {"bool": {"must": [{"match": {"text": command[i]}} for i in range(2, len(command))]}}
                       ]
                   }
               }
               }
        res = es.search(index="kaftar", doc_type="message", body=doc)
        try:
            res = res['hits']
            res = res['hits']
            sender = []
            time = []
            date = []
            textOfMessage = []
            for x in res:
                temp = x['_source']
                try:
                    sender.append(temp['sender'])
                    time.append(temp['time'])
                    date.append(temp['date'])
                    textOfMessage.append(temp['text'])
                except KeyError:
                    pass
            printMessage(sender, textOfMessage, time, date)
        except KeyError:
            pass
    elif command[0] == "search_group_by_sender":
        all_groups, _, __ = findGroupsAndChannels(es, user)
        if command[1] not in all_groups:
            print("Access denied.")
            continue
        doc = {"size": 1000,
               "query": {
                   "bool": {
                       "must": [
                           {"bool": {"must": {"match": {"group": str(command[1])}}}},
                           {"bool": {"must": {"match": {"sender": str(command[2])}}}},
                           {"bool": {"must": [{"match": {"text": command[i]}} for i in range(3, len(command))]}}
                       ]
                   }
               }
               }
        res = es.search(index="kaftar", doc_type="message", body=doc)
        try:
            res = res['hits']
            res = res['hits']
            sender = []
            time = []
            date = []
            textOfMessage = []
            for x in res:
                temp = x['_source']
                try:
                    sender.append(temp['sender'])
                    time.append(temp['time'])
                    date.append(temp['date'])
                    textOfMessage.append(temp['text'])
                except KeyError:
                    pass
            printMessage(sender, textOfMessage, time, date)
        except KeyError:
            pass
    elif command[0] == "search_all_fuzzy":
        all_groups, all_channels, all = findGroupsAndChannels(es, user)
        if all_channels and all_groups:
            doc = {"size": 1000,
                "query": {
                    "bool": {
                        "must": [
                            {"bool": {"should": [{"bool": {"must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}},{"match": {"channel": "NONE"}}]}}] +
                                                [{"bool": {
                                                    "must": [{"match": {"receiver": str(user)}}, {"match": {"group": "NONE"}},
                                                             {"match": {"channel": "NONE"}}]}}] +
                                       [{"match": {"group": x}} for x in all_groups] +
                                    [{"match": {"channel": x}} for x in all_channels]}},
                            {"bool": {"must": [{"match": {"text": {"query": command[i], "fuzziness": "AUTO"}}} for i in range(1, len(command))]}}

                        ]
                    }
                }
            }
        elif all_groups:
            doc = {"size": 1000,
                   "query": {
                       "bool": {
                           "must": [
                               {"bool": {"should": [{"bool": {
                                   "must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}},
                                            {"match": {"channel": "NONE"}}]}}] +
                                                   [{"bool": {
                                                       "must": [{"match": {"receiver": str(user)}},
                                                                {"match": {"group": "NONE"}},
                                                                {"match": {"channel": "NONE"}}]}}] +
                                                   [{"match": {"group": x}} for x in all_groups]}},
                               {"bool": {"must": [{"match": {"text": {"query": command[i], "fuzziness": "AUTO"}}} for i in
                                                             range(1, len(command))]}}
                           ]
                       }
                   }
                   }
        elif all_channels:
            doc = {"size": 1000,
                   "query": {
                       "bool": {
                           "must": [
                               {"bool": {"should": [{"bool": {
                                   "must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}},
                                            {"match": {"channel": "NONE"}}]}}] +
                                                   [{"bool": {
                                                       "must": [{"match": {"receiver": str(user)}},
                                                                {"match": {"group": "NONE"}},
                                                                {"match": {"channel": "NONE"}}]}}] +
                                                   [{"match": {"channel": x for x in all_channels}}]}},
                               {"bool": {"must": [{"match": {"text": {"query": command[i], "fuzziness": "AUTO"}}} for i in
                                                             range(1, len(command))]}}
                           ]
                       }
                   }
                   }
        else:
            doc = {"size": 1000,
                   "query": {
                       "bool": {
                           "must": [
                               {"bool": {"should": [{"bool": {
                                   "must": [{"match": {"sender": str(user)}}, {"match": {"group": "NONE"}},
                                            {"match": {"channel": "NONE"}}]}}] +
                                                   [{"bool": {
                                                       "must": [{"match": {"receiver": str(user)}},
                                                                {"match": {"group": "NONE"}},
                                                                {"match": {"channel": "NONE"}}]}}]}},
                               {"bool": {"must": [{"match": {"text": {"query": command[i], "fuzziness": "AUTO"}}} for i in
                                                             range(1, len(command))]}}
                           ]
                       }
                   }
                   }
        res = es.search(index="kaftar", doc_type="message", body=doc)
        try:
            res = res['hits']
            res = res['hits']
            sender = []
            time = []
            date = []
            textOfMessage = []
            for x in res:
                temp = x['_source']
                try:
                    sender.append(temp['sender'])
                    time.append(temp['time'])
                    date.append(temp['date'])
                    textOfMessage.append(temp['text'])
                except KeyError:
                    pass
            printMessage(sender, textOfMessage, time, date)
        except KeyError:
            pass
    elif command[0] == "view_messages_by_date":
        all_groups, all_channels, all = findGroupsAndChannels(es, user)
        # print(user)
        # print(len(all) if all is not None else "is None")
        if all_channels and all_groups:
            doc = {"query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"bool": {
                                    "must": [{"match": {"sender": str(user)}},
                                             {"match": {"group": "NONE"}},
                                             {"match": {"channel": "NONE"}}]
                                }
                                },
                                {"bool": {
                                    "must": [{"match": {"receiver": str(user)}},
                                             {"match": {"group": "NONE"}},
                                             {"match": {"channel": "NONE"}}]
                                }
                                },
                                [{"match": {"group": x}} for x in all_groups],
                                [{"match": {"channel": x}} for x in all_channels]
                            ]
                        }},
                        {"bool": {
                            "must": {"match": {"date": command[1]}}
                        }}
                    ]
                }
            },
                "size": 1000
            }
        elif all_groups:
            doc = {"query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"bool": {
                                    "must": [{"match": {"sender": str(user)}},
                                             {"match": {"group": "NONE"}},
                                             {"match": {"channel": "NONE"}}]
                                }
                                },
                                {"bool": {
                                    "must": [{"match": {"receiver": str(user)}},
                                             {"match": {"group": "NONE"}},
                                             {"match": {"channel": "NONE"}}]
                                }
                                },
                                [{"match": {"group": x}} for x in all_groups]
                            ]
                        }},
                        {"bool": {
                            "must": {"match": {"date": command[1]}}
                        }}
                    ]
                }
            },
                "size": 1000
            }
        elif all_channels:
            doc = {"query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"bool": {
                                    "must": [{"match": {"sender": str(user)}},
                                             {"match": {"group": "NONE"}},
                                             {"match": {"channel": "NONE"}}]
                                }
                                },
                                {"bool": {
                                    "must": [{"match": {"receiver": str(user)}},
                                             {"match": {"group": "NONE"}},
                                             {"match": {"channel": "NONE"}}]
                                }
                                },
                                [{"match": {"channel": x}} for x in all_channels]
                            ]
                        }},
                        {"bool": {
                            "must": {"match": {"date": command[1]}}
                        }}
                    ]
                }
            },
                "size": 1000
            }
        else:
            doc = {"query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"bool": {
                                    "must": [{"match": {"sender": str(user)}},
                                             {"match": {"group": "NONE"}},
                                             {"match": {"channel": "NONE"}}]
                                    }
                                },
                                {"bool": {
                                    "must": [{"match": {"receiver": str(user)}},
                                             {"match": {"group": "NONE"}},
                                             {"match": {"channel": "NONE"}}]
                                    }
                                }
                            ]
                        }},
                        {"bool": {
                            "must": {"match": {"date": command[1]}}
                        }}
                    ]
                }
            },
                "size": 1000
            }
        res = es.search(index="kaftar", doc_type="message", body=doc)
        try:
            res = res['hits']
            res = res['hits']
            sender = []
            time = []
            date = []
            textOfMessage = []
            for x in res:
                temp = x['_source']
                try:
                    sender.append(temp['sender'])
                    time.append(temp['time'])
                    date.append(temp['date'])
                    textOfMessage.append(temp['text'])
                except KeyError:
                    pass
            printMessage(sender, textOfMessage, time, date)
        except KeyError:
            pass
    elif command[0] == "view_messages_by_date_chat":
        doc = {"query": {
            "bool": {
                "must": [
                    {"bool": {
                        "should": [
                            {"bool": {
                                "must": [{"match": {"sender": str(user)}},
                                         {"match": {"receiver": command[1]}},
                                         {"match": {"group": "NONE"}},
                                         {"match": {"channel": "NONE"}}]
                            }
                            },
                            {"bool": {
                                "must": [{"match": {"sender": command[1]}},
                                         {"match": {"receiver": str(user)}},
                                         {"match": {"group": "NONE"}},
                                         {"match": {"channel": "NONE"}}]
                            }
                            }
                        ]
                    }},
                    {"bool": {
                        "must": {"match": {"date": command[2]}}
                    }}
                ]
            }
        },
            "size": 1000
        }
        res = es.search(index="kaftar", doc_type="message", body=doc)
        try:
            res = res['hits']
            res = res['hits']
            sender = []
            time = []
            date = []
            textOfMessage = []
            for x in res:
                temp = x['_source']
                try:
                    sender.append(temp['sender'])
                    time.append(temp['time'])
                    date.append(temp['date'])
                    textOfMessage.append(temp['text'])
                except KeyError:
                    pass
            printMessage(sender, textOfMessage, time, date)
        except KeyError:
            pass
    elif command[0] == "view_messages_by_date_group":
        all_groups, all_channels, all = findGroupsAndChannels(es, user)
        if command[1] not in all_groups:
            print("Access denied.")
            continue
        if all_groups:
            doc = {"query": {
                "bool": {
                    "must": [
                        {"match": {"group": command[1]}},
                        {"match": {"date": command[2]}}
                    ]
                }
            },
                "size": 1000
            }
            res = es.search(index="kaftar", doc_type="message", body=doc)
            try:
                res = res['hits']
                res = res['hits']
                sender = []
                time = []
                date = []
                textOfMessage = []
                for x in res:
                    temp = x['_source']
                    try:
                        sender.append(temp['sender'])
                        time.append(temp['time'])
                        date.append(temp['date'])
                        textOfMessage.append(temp['text'])
                    except KeyError:
                        pass
                printMessage(sender, textOfMessage, time, date)
            except KeyError:
                pass
    elif command[0] == "view_messages_by_date_channel":
        all_groups, all_channels, all = findGroupsAndChannels(es, user)
        if command[1] not in all_channels:
            print("Access denied.")
            continue
        if all_channels:
            doc = {"query": {
                "bool": {
                    "must": [
                        {"match": {"channel": command[1]}},
                        {"match": {"date": command[2]}}
                    ]
                }
            },
                "size": 1000
            }
            res = es.search(index="kaftar", doc_type="message", body=doc)
            try:
                res = res['hits']
                res = res['hits']
                sender = []
                time = []
                date = []
                textOfMessage = []
                for x in res:
                    temp = x['_source']
                    try:
                        sender.append(temp['sender'])
                        time.append(temp['time'])
                        date.append(temp['date'])
                        textOfMessage.append(temp['text'])
                    except KeyError:
                        pass
                printMessage(sender, textOfMessage, time, date)
            except KeyError:
                pass