SELECT District
FROM (SELECT District, CountryCode
      FROM world.city AS ci
      WHERE District IN (SELECT District FROM world.country AS k, world.city AS c_two WHERE k.Capital=c_two.ID)
      GROUP BY District
      HAVING SUM(ci.Population) > (SELECT SUM(L.Percentage/100 * co.Population) FROM world.countrylanguage AS L, world.country AS co WHERE L.CountryCode=co.Code and L.CountryCode=ci.CountryCode and L.IsOfficial=TRUE GROUP BY L.CountryCode)) AS temp ORDER BY temp.District;

#Q9
SELECT Continent, TRUNCATE(AVG((GNP/Population)*(POWER(1.1, FLOOR(LifeExpectancy)+1)-1)*10), 5) AS ExpectedIncome
FROM world.country
GROUP BY Continent
ORDER BY ExpectedIncome;