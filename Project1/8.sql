/*Query8*/
SELECT ID
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
ORDER BY MAX(Send_Time) DESC;