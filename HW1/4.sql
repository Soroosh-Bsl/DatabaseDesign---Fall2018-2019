SELECT DISTINCT Name
FROM world.country AS co1
WHERE (GovernmentForm LIKE '%Republic%' or GovernmentForm LIKE '%republic') and Code NOT IN(SELECT co2.Code FROM world.country AS co2, world.countrylanguage AS L2 WHERE co2.Code=L2.CountryCode and L2.IsOfficial=TRUE and L2.Percentage >= 20) and EXISTS(SELECT * FROM world.country AS co3, world.countrylanguage AS L3 WHERE co3.Code= co1.Code and co3.Code=L3.CountryCode and L3.IsOfficial=TRUE )
ORDER BY Name;