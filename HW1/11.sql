SELECT country.Name, COUNT(*) AS LangNumber
FROM world.country, world.countrylanguage
WHERE Code IN (SELECT ci.CountryCode
FROM world.city AS ci
WHERE ci.Name='Victoria') and Code=CountryCode
GROUP BY country.Name
ORDER BY LangNumber DESC;