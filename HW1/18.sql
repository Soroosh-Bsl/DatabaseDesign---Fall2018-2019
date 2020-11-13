SELECT Region, ROUND(AVG(Population/SurfaceArea), 3) AS Density
FROM world.country
GROUP BY Region
ORDER BY Density DESC;