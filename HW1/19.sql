SELECT x.Continent, x.Language, x.LangPopulation
FROM (SELECT co1.Continent, L1.Language, ROUND(SUM(co1.Population*L1.Percentage/100)) AS LangPopulation
      FROM world.country AS co1, world.countrylanguage AS L1
      WHERE L1.CountryCode=co1.Code and L1.IsOfficial<>TRUE
      GROUP BY  co1.Continent, L1.Language) AS x
WHERE x.LangPopulation >= ALL(SELECT y.LangPopulation FROM (SELECT co2.Continent, ROUND(SUM(co2.Population*L2.Percentage/100)) AS LangPopulation
                              FROM world.country AS co2, world.countrylanguage AS L2
                              WHERE L2.CountryCode=co2.Code and L2.IsOfficial<>TRUE
                              GROUP BY  co2.Continent, L2.Language) AS y
                              WHERE x.Continent = y.Continent)
ORDER BY x.LangPopulation DESC ;