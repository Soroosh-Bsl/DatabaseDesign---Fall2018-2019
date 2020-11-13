SELECT DISTINCT L1.Language
FROM world.country AS co, world.countrylanguage AS L1
WHERE co.Code=L1.CountryCode
GROUP BY L1.Language
HAVING MAX(IsOfficial)<>TRUE
ORDER BY L1.Language;