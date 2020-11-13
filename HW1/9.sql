SELECT Continent, TRUNCATE(AVG((GNP/Population)*(POWER(1.1, FLOOR(LifeExpectancy)+1)-1)*10), 5) AS ExpectedIncome
FROM world.country
GROUP BY Continent
ORDER BY ExpectedIncome;