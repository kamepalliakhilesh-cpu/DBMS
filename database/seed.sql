-- =======================================================
-- DISASTER RELIEF RESOURCE MANAGEMENT SYSTEM
-- Seed Sample Data (MySQL)
-- Matches Project Documentation & Presentation
-- =======================================================

USE disaster_relief_db;

-- Clear any existing records safely
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Distribution;
TRUNCATE TABLE Volunteer;
TRUNCATE TABLE Resource;
TRUNCATE TABLE ReliefCenter;
TRUNCATE TABLE Victim;
TRUNCATE TABLE Disaster;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. INSERT DISASTERS
INSERT INTO Disaster (Disaster_ID, Type, Location, Date, Severity_Level) VALUES
(1, 'Cyclone', 'Kakinada', '2026-10-10', 'High'),
(2, 'Flood', 'Vijayawada', '2026-09-15', 'Critical'),
(3, 'Earthquake', 'Visakhapatnam', '2026-08-20', 'Moderate'),
(4, 'Landslide', 'Araku Valley', '2026-07-05', 'High'),
(5, 'Tsunami Warning', 'Machilipatnam', '2026-11-01', 'Low');

-- 2. INSERT VICTIMS
INSERT INTO Victim (Victim_ID, Name, Age, Contact, Address, Disaster_ID) VALUES
(101, 'Ravi Kumar', 35, '9876543210', 'Main Bazaar, Kakinada', 1),
(102, 'Priya Devi', 29, '9876543211', 'Port Road, Kakinada', 1),
(103, 'Suresh Reddy', 42, '9876543212', 'Krishna Riverbank, Vijayawada', 2),
(104, 'Lakshmi Bai', 50, '9876543213', 'Governorpet, Vijayawada', 2),
(105, 'Anil Varma', 24, '9876543214', 'Beach Road, Visakhapatnam', 3),
(106, 'Kavitha S.', 31, '9876543215', 'Tribal Colony, Araku Valley', 4);

-- 3. INSERT RELIEF CENTERS
INSERT INTO ReliefCenter (Center_ID, Name, Location, Capacity, Contact) VALUES
(401, 'Relief Centre 1', 'Collectorate Grounds, Kakinada', 500, '9876000001'),
(402, 'Relief Centre 2 - Krishna', 'Indira Gandhi Stadium, Vijayawada', 800, '9876000002'),
(403, 'Coastal Shelter Hub', 'Andhra University Campus, Visakhapatnam', 450, '9876000003'),
(404, 'Hill Rescue Camp', 'Paderu Junction, Araku Valley', 300, '9876000004');

-- 4. INSERT RESOURCES
INSERT INTO Resource (Resource_ID, Resource_Name, Type, Quantity, Center_ID) VALUES
(201, 'Drinking Water', 'Water', 500, 401),
(202, 'Rice', 'Food', 250, 401),
(203, 'Medical Kit', 'Medical', 100, 401),
(204, 'Baby Food Packets', 'Food', 180, 402),
(205, 'Blankets & Tarpaulins', 'Shelter', 350, 402),
(206, 'First Aid Essentials', 'Medical', 90, 403),
(207, 'Canned Meals', 'Food', 400, 404);

-- 5. INSERT VOLUNTEERS
INSERT INTO Volunteer (Volunteer_ID, Name, Phone, Skill, Center_ID) VALUES
(301, 'Arjun Kumar', '9876500001', 'Medical Support', 401),
(302, 'Sneha Rao', '9876500002', 'Food Distribution', 401),
(303, 'Manoj Verma', '9876500003', 'Rescue & Evacuation', 402),
(304, 'Divya Teja', '9876500004', 'Medical Support', 403),
(305, 'Rajesh Patel', '9876500005', 'Logistics & Transport', 404);

-- 6. INSERT DISTRIBUTIONS
INSERT INTO Distribution (Distribution_ID, Victim_ID, Resource_ID, Quantity_Distributed, Date) VALUES
(701, 101, 203, 5, '2026-10-10'),
(702, 102, 201, 10, '2026-10-10'),
(703, 103, 204, 8, '2026-09-16'),
(704, 104, 205, 4, '2026-09-16'),
(705, 105, 206, 3, '2026-08-21'),
(706, 106, 207, 12, '2026-07-06');
