SELECT DISTINCT District
FROM world.city AS c
GROUP BY District
HAVING (SELECT COUNT(*) FROM world.country AS k WHERE k.Population < SUM(c.Population)) >= 15
ORDER BY District;