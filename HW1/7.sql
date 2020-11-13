SELECT District
FROM world.city AS c_one
WHERE District NOT IN (SELECT c_two.District FROM world.country AS k, world.city AS c_two WHERE k.Capital=c_two.ID and k.Code = c_two.CountryCode)
GROUP BY District
ORDER BY SUM(Population) DESC LIMIT 1;