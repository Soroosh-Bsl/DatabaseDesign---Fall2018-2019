SELECT temp.Language, ROUND(LangPopulation/100) AS LangPopulation
FROM ((SELECT Language, SUM(L1.Percentage * co1.Population) AS LangPopulation
FROM world.countrylanguage AS L1, world.country AS co1
WHERE L1.CountryCode=co1.Code
GROUP BY Language ORDER BY LangPopulation DESC LIMIT 5) UNION
    (SELECT Language, SUM(L1.Percentage * co1.Population) AS LangPopulation
FROM world.countrylanguage AS L1, world.country AS co1
WHERE L1.CountryCode=co1.Code
GROUP BY Language ORDER BY LangPopulation ASC LIMIT 5)) AS temp
ORDER BY temp.LangPopulation DESC;