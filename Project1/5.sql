/* Query 5 */
SELECT MGroup.Group_ID, Group_Link, Group_Dest, Group_Name, Bio, Self_Destruct
FROM MGroup
JOIN Group_Settings S on MGroup.Group_ID = S.Group_ID
WHERE MGroup.Group_ID = 'kharrazi';