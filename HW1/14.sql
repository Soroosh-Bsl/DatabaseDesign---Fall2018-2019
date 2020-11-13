SELECT DISTINCT L1.Language
FROM world.countrylanguage AS L1
WHERE L1.Language NOT IN(SELECT DISTINCT Language FROM world.countrylanguage AS L2 WHERE L2.IsOfficial=TRUE)
ORDER BY L1.Language;