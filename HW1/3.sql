SELECT ROUND(100*SUM(Population)/(SELECT SUM(c.Population) FROM world.country AS c), 5)
FROM world.country, world.countrylanguage
WHERE CountryCode=Code and Language='English' and IsOfficial=TRUE;