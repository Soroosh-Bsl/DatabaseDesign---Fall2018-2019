/*Query4*/
SELECT Channel.Channel_ID,Channel_Name,Channel_Link,Channel_Dest,Bio
FROM Channel,Channel_Settings
WHERE Channel_Settings.Channel_ID = Channel.Channel_ID AND Channel.Channel_ID = 'konkur';