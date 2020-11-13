SELECT ROUND(GNP/Population, 3) AS Income
FROM world.country
WHERE Name='Iran' and (HeadOfState LIKE '%Khatami%' or HeadOfState LIKE '%khatami');