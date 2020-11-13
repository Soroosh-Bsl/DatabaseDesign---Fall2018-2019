#3
SELECT Text, Sender_ID
FROM Message
WHERE (Sender_ID='Ashkansoli' and Message_ID IN (SELECT Receiver_Message.Message_ID FROM Receiver_Message WHERE Receiver_Message.Receiver_ID = 'Sorooshbsl')) OR
      (Sender_ID='Sorooshbsl' and Message_ID IN (SELECT Receiver_Message.Message_ID FROM Receiver_Message WHERE Receiver_Message.Receiver_ID = 'Ashkansoli'))
ORDER BY Send_Time;