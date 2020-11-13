SELECT DISTINCT Language
FROM world.countrylanguage AS L1
WHERE NOT EXISTS(SELECT * FROM world.countrylanguage AS L2 WHERE L1.Language=L2.Language and L2.IsOfficial=TRUE )
ORDER BY L1.Language;