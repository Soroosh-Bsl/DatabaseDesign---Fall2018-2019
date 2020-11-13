SELECT Name
FROM world.country
WHERE NOT EXISTS(SELECT * FROM world.countrylanguage WHERE CountryCode=Code AND IsOfficial=TRUE)
ORDER BY Name;