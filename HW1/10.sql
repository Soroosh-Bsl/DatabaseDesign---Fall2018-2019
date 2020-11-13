SELECT co1.Name, ci_one.Name, ci_one.Population
FROM world.city AS ci_one, world.country AS co1
WHERE co1.Code=ci_one.CountryCode and ci_one.CountryCode IN (SELECT co2.Code
                            FROM world.country AS co2
                            WHERE co2.Code IN (SELECT L.CountryCode FROM world.countrylanguage AS L WHERE L.Language='English')) and (SELECT COUNT(*) FROM world.city AS ci_two WHERE ci_two.CountryCode=ci_one.CountryCode and ci_two.Population > ci_one.Population) = 4
ORDER BY ci_one.Population DESC ;