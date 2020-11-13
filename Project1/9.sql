#9
SELECT selfChatter.ID, Number_Of_Notifs
FROM (SELECT ID, MAX(Send_Time) AS Last_Time
FROM (((SELECT DISTINCT Group_ID as ID, Send_Time
       FROM Group_Message as GM
          JOIN Message M on GM.Message_ID = M.Message_ID
       WHERE M.Sender_ID = 'Sorooshbsl' OR 'Sorooshbsl' IN (
            SELECT Member_ID
            FROM Group_Enrollment
            WHERE Group_Enrollment.Group_ID=GM.Group_ID
           )
       UNION
       SELECT DISTINCT Channel_ID as ID, Send_Time
       FROM Channel_Messages as CM
          JOIN Message M2 on CM.Message_ID = M2.Message_ID
       WHERE M2.Sender_ID = 'Sorooshbsl' OR 'Sorooshbsl' IN(
            SELECT Member_ID
            FROM Channel_Members
            WHERE Channel_Members.Channel_ID=CM.Channel_ID
           )
      ) UNION (SELECT DISTINCT Sender_ID as ID, Send_Time
                FROM Message
                  JOIN Receiver_Message Message2 on Message.Message_ID = Message2.Message_ID
                WHERE Receiver_ID = 'Sorooshbsl'
               ) UNION (
                SELECT DISTINCT Receiver_ID as ID, Send_Time
                FROM Receiver_Message
                  JOIN Message M3 on Receiver_Message.Message_ID = M3.Message_ID
                WHERE Sender_ID = 'Sorooshbsl')
          )
       ORDER BY Send_Time DESC
    ) as selfChat

WHERE ID NOT IN (SELECT Blocked_ID FROM Blocked_User WHERE Blocker_ID='Sorooshbsl')
GROUP BY ID
ORDER BY Last_Time DESC) AS selfChatter,
     ((SELECT Channel_Members.Channel_ID AS ID , COUNT(*) AS Number_Of_Notifs
FROM Channel_Members, Channel_Messages
WHERE Channel_Members.Member_ID='Sorooshbsl' and Channel_Members.Channel_ID=Channel_Messages.Channel_ID and Channel_Messages.Message_ID NOT IN (SELECT Seen_Messages.Message_ID FROM Seen_Messages WHERE Seen_Messages.User_ID='Sorooshbsl')
GROUP BY Channel_Members.Channel_ID)
UNION
    (SELECT Group_Enrollment.Group_ID AS ID, COUNT(*) AS Number_Of_Notifs
FROM Group_Enrollment, Group_Message
WHERE Group_Enrollment.Member_ID='Sorooshbsl' and Group_Enrollment.Group_ID=Group_Message.Group_ID and Group_Message.Message_ID NOT IN (SELECT Seen_Messages.Message_ID FROM Seen_Messages WHERE Seen_Messages.User_ID='Sorooshbsl')
GROUP BY Group_Enrollment.Group_ID)
UNION
    (SELECT Message.Sender_ID AS ID, COUNT(*) AS Number_Of_Notifs
FROM Message, Receiver_Message
WHERE Receiver_Message.Receiver_ID='Sorooshbsl' and Receiver_Message.Message_ID=Message.Message_ID and Receiver_Message.Seen=FALSE
GROUP BY Message.Sender_ID)) AS Counts_Table

WHERE selfChatter.ID=Counts_Table.ID
ORDER BY selfChatter.Last_Time DESC;