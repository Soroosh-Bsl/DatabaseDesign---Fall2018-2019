SELECT city.Name
FROM world.country, world.city
WHERE CountryCode=Code and Capital<>ID
ORDER BY city.Population DESC LIMIT 1;