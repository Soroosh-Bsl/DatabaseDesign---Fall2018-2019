SELECT Name, Population, SurfaceArea
FROM world.country
WHERE Continent IN (SELECT DISTINCT Continent FROM world.country WHERE Name='Iran') and Population > (SELECT DISTINCT Population FROM world.country WHERE Name='Iran') and SurfaceArea > (SELECT DISTINCT SurfaceArea FROM world.country WHERE Name='Iran')
ORDER BY Population DESC;