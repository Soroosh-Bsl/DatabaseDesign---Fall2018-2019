/* Query 2 */
SELECT Text, Sender_ID
FROM Message
WHERE Message_ID IN (SELECT Message_ID
                    FROM Group_Message
                    WHERE Group_ID = 'rohban')
ORDER BY Send_Time;