/*Query1*/
SELECT Text
FROM Message
WHERE Message_ID IN (SELECT Message_ID
                    FROM Channel_Messages
                    WHERE Channel_ID = 'emoji')
ORDER BY Send_Time;