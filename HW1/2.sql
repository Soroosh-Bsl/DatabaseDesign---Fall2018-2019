SELECT CountryCode, city.Name, ROUND(city.Population*100/country.Population, 5) AS Percentage
FROM world.country, world.city
WHERE Capital=ID and CountryCode=Code
ORDER BY Code DESC;