-- =======================================================
-- DISASTER RELIEF RESOURCE MANAGEMENT SYSTEM
-- Academic SQL Queries (Q1 to Q20)
-- From Project Report & Viva Reference
-- =======================================================

USE disaster_relief_db;

-- Q1. Display all disasters
SELECT * FROM Disaster;

-- Q2. Display all victims
SELECT * FROM Victim;

-- Q3. Display all resources
SELECT * FROM Resource;

-- Q4. Display all volunteers
SELECT * FROM Volunteer;

-- Q5. Display all relief centres
SELECT * FROM ReliefCenter;

-- Q6. Resources with quantity greater than 0
SELECT Resource_Name, Type, Quantity FROM Resource WHERE Quantity > 0;

-- Q7. Victims sorted by name alphabetically
SELECT * FROM Victim ORDER BY Name;

-- Q8. Victims linked to a disaster (Disaster_ID = 1)
SELECT V.Victim_ID, V.Name, V.Age, V.Contact, D.Type, D.Location 
FROM Victim V 
JOIN Disaster D ON V.Disaster_ID = D.Disaster_ID 
WHERE D.Disaster_ID = 1;

-- Q9. Resources with their relief centre
SELECT R.Resource_Name, R.Type, R.Quantity, C.Name AS Centre_Name 
FROM Resource R 
JOIN ReliefCenter C ON R.Center_ID = C.Center_ID;

-- Q10. Volunteers assigned to a centre
SELECT V.Name, V.Phone, V.Skill, C.Name AS Centre_Name 
FROM Volunteer V 
JOIN ReliefCenter C ON V.Center_ID = C.Center_ID;

-- Q11. Distribution details with victim and resource
SELECT Dist.Distribution_ID, V.Name AS Victim_Name, R.Resource_Name, Dist.Quantity_Distributed, Dist.Date 
FROM Distribution Dist 
JOIN Victim V ON Dist.Victim_ID = V.Victim_ID 
JOIN Resource R ON Dist.Resource_ID = R.Resource_ID;

-- Q12. Count of victims per disaster
SELECT D.Type, COUNT(V.Victim_ID) AS Victim_Count 
FROM Disaster D 
LEFT JOIN Victim V ON D.Disaster_ID = V.Disaster_ID 
GROUP BY D.Type;

-- Q13. Total quantity distributed per resource
SELECT R.Resource_Name, SUM(Dist.Quantity_Distributed) AS Total_Distributed 
FROM Distribution Dist 
JOIN Resource R ON Dist.Resource_ID = R.Resource_ID 
GROUP BY R.Resource_Name;

-- Q14. Disasters of type Cyclone
SELECT * FROM Disaster WHERE Type = 'Cyclone';

-- Q15. Resources of type Food
SELECT * FROM Resource WHERE Type = 'Food';

-- Q16. Volunteers with medical skill
SELECT * FROM Volunteer WHERE Skill LIKE '%Medical%';

-- Q17. Victims whose names start with 'R'
SELECT * FROM Victim WHERE Name LIKE 'R%';

-- Q18. Relief centres with capacity greater than 100
SELECT * FROM ReliefCenter WHERE Capacity > 100;

-- Q19. Update resource quantity
UPDATE Resource SET Quantity = Quantity + 200 WHERE Resource_ID = 201;

-- Q20. Delete a distribution record
DELETE FROM Distribution WHERE Distribution_ID = 702;
