SELECT Name, Population, CountryCode
FROM world.city AS ci_two
WHERE ci_two.CountryCode IN (SELECT co_one.Code
FROM world.country AS co_one, world.city AS ci_one
WHERE co_one.Code=ci_one.CountryCode
GROUP BY co_one.Name
HAVING COUNT(ci_one.Name) < 3) and ci_two.Population >= ALL(SELECT ci_three.Population FROM world.city AS ci_three WHERE ci_two.CountryCode=ci_three.CountryCode)
ORDER BY Population DESC;