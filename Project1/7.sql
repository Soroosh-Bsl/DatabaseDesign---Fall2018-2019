/*Query7*/
SELECT COUNT(Text) AS Cnt
FROM Message
WHERE Message_ID IN (SELECT Message_ID FROM Group_Message WHERE Group_ID IN (SELECT Group_ID FROM Group_Enrollment WHERE Member_ID = 'Sorooshbsl')
        AND Message_ID NOT IN (SELECT Message_ID FROM Seen_Messages WHERE User_ID = 'Sorooshbsl'))
OR Message_ID IN (SELECT Message_ID FROM Channel_Messages WHERE Channel_ID IN (SELECT Channel_ID FROM Channel_Members WHERE Member_ID = 'Sorooshbsl')
        AND Message_ID NOT IN (SELECT Message_ID FROM Seen_Messages WHERE User_ID = 'Sorooshbsl'))
OR Message_ID IN (SELECT Message_ID FROM Receiver_Message
                  WHERE Receiver_ID = 'Sorooshbsl' AND Seen = FALSE AND Sender_ID NOT IN
                                                                        (SELECT Blocked_ID FROM Blocked_User WHERE Blocker_ID = 'Sorooshbsl'));