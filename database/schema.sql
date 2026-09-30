-- =======================================================
-- DISASTER RELIEF RESOURCE MANAGEMENT SYSTEM
-- Relational Database Schema (MySQL)
-- Aligned with Project Documentation & Presentation
-- =======================================================

CREATE DATABASE IF NOT EXISTS disaster_relief_db;
USE disaster_relief_db;

-- Drop tables in reverse dependency order if they exist
DROP TABLE IF EXISTS Distribution;
DROP TABLE IF EXISTS Volunteer;
DROP TABLE IF EXISTS Resource;
DROP TABLE IF EXISTS ReliefCenter;
DROP TABLE IF EXISTS Victim;
DROP TABLE IF EXISTS Disaster;

-- 1. DISASTER TABLE
CREATE TABLE Disaster (
    Disaster_ID INT PRIMARY KEY,
    Type VARCHAR(50) NOT NULL,
    Location VARCHAR(100),
    Date DATE,
    Severity_Level VARCHAR(20)
);

-- 2. VICTIM TABLE
CREATE TABLE Victim (
    Victim_ID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Age INT,
    Contact VARCHAR(15),
    Address VARCHAR(200),
    Disaster_ID INT,
    CONSTRAINT fk_victim_disaster
        FOREIGN KEY (Disaster_ID)
        REFERENCES Disaster(Disaster_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- 3. RELIEF CENTER TABLE
CREATE TABLE ReliefCenter (
    Center_ID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Location VARCHAR(150),
    Capacity INT,
    Contact VARCHAR(15)
);

-- 4. RESOURCE TABLE
CREATE TABLE Resource (
    Resource_ID INT PRIMARY KEY,
    Resource_Name VARCHAR(100) NOT NULL,
    Type VARCHAR(50),
    Quantity INT NOT NULL,
    Center_ID INT,
    CONSTRAINT fk_resource_center
        FOREIGN KEY (Center_ID)
        REFERENCES ReliefCenter(Center_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- 5. VOLUNTEER TABLE
CREATE TABLE Volunteer (
    Volunteer_ID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Phone VARCHAR(15),
    Skill VARCHAR(100),
    Center_ID INT,
    CONSTRAINT fk_volunteer_center
        FOREIGN KEY (Center_ID)
        REFERENCES ReliefCenter(Center_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- 6. DISTRIBUTION TABLE
CREATE TABLE Distribution (
    Distribution_ID INT PRIMARY KEY,
    Victim_ID INT,
    Resource_ID INT,
    Quantity_Distributed INT NOT NULL,
    Date DATE,
    CONSTRAINT fk_dist_victim
        FOREIGN KEY (Victim_ID)
        REFERENCES Victim(Victim_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_dist_resource
        FOREIGN KEY (Resource_ID)
        REFERENCES Resource(Resource_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
