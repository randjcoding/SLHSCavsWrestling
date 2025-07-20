-- =====================================================
-- SOUTHERN LEE WRESTLING - DROPLET SETUP
-- =====================================================
-- Run this SQL on the droplet PostgreSQL database
-- This contains ONLY what's needed for deployment

-- Step 1: Check current state
SELECT 'Current Weight Classes' as info, division, COUNT(*) as count 
FROM weightClasses 
WHERE active = TRUE 
GROUP BY division 
ORDER BY division;

-- Step 2: Insert basic weight classes (using correct column names: name, max_weight)
INSERT INTO weightClasses (name, max_weight, division, level, active) 
SELECT * FROM (VALUES 
    ('106 lbs NC High School Boys', 106, 'NC High School Boys', 'Varsity', true),
    ('113 lbs NC High School Boys', 113, 'NC High School Boys', 'Varsity', true),
    ('120 lbs NC High School Boys', 120, 'NC High School Boys', 'Varsity', true),
    ('126 lbs NC High School Boys', 126, 'NC High School Boys', 'Varsity', true),
    ('132 lbs NC High School Boys', 132, 'NC High School Boys', 'Varsity', true),
    ('138 lbs NC High School Boys', 138, 'NC High School Boys', 'Varsity', true),
    ('144 lbs NC High School Boys', 144, 'NC High School Boys', 'Varsity', true),
    ('150 lbs NC High School Boys', 150, 'NC High School Boys', 'Varsity', true),
    ('157 lbs NC High School Boys', 157, 'NC High School Boys', 'Varsity', true),
    ('165 lbs NC High School Boys', 165, 'NC High School Boys', 'Varsity', true),
    ('175 lbs NC High School Boys', 175, 'NC High School Boys', 'Varsity', true),
    ('190 lbs NC High School Boys', 190, 'NC High School Boys', 'Varsity', true),
    ('215 lbs NC High School Boys', 215, 'NC High School Boys', 'Varsity', true),
    ('285 lbs NC High School Boys', 285, 'NC High School Boys', 'Varsity', true),
    
    ('100 lbs NC High School Girls', 100, 'NC High School Girls', 'Varsity', true),
    ('105 lbs NC High School Girls', 105, 'NC High School Girls', 'Varsity', true),
    ('110 lbs NC High School Girls', 110, 'NC High School Girls', 'Varsity', true),
    ('115 lbs NC High School Girls', 115, 'NC High School Girls', 'Varsity', true),
    ('120 lbs NC High School Girls', 120, 'NC High School Girls', 'Varsity', true),
    ('125 lbs NC High School Girls', 125, 'NC High School Girls', 'Varsity', true),
    ('130 lbs NC High School Girls', 130, 'NC High School Girls', 'Varsity', true),
    ('135 lbs NC High School Girls', 135, 'NC High School Girls', 'Varsity', true),
    ('140 lbs NC High School Girls', 140, 'NC High School Girls', 'Varsity', true),
    ('145 lbs NC High School Girls', 145, 'NC High School Girls', 'Varsity', true),
    ('155 lbs NC High School Girls', 155, 'NC High School Girls', 'Varsity', true),
    ('170 lbs NC High School Girls', 170, 'NC High School Girls', 'Varsity', true),
    ('190 lbs NC High School Girls', 190, 'NC High School Girls', 'Varsity', true),
    ('200 lbs NC High School Girls', 200, 'NC High School Girls', 'Varsity', true)
) AS v(name, max_weight, division, level, active)
WHERE NOT EXISTS (
    SELECT 1 FROM weightClasses 
    WHERE division = v.division AND max_weight = v.max_weight
);

-- Step 3: Update any existing data to consistent division naming
UPDATE weightClasses 
SET division = 'NC High School Boys' 
WHERE division IN ('Boys', 'North Carolina Boys', 'High School Boys');

UPDATE weightClasses 
SET division = 'NC High School Girls' 
WHERE division IN ('Girls', 'North Carolina Girls', 'High School Girls');

-- Step 4: Update any existing wrestlers to match
UPDATE wrestlers 
SET division = 'NC High School Boys' 
WHERE division IN ('Boys', 'North Carolina Boys', 'High School Boys');

UPDATE wrestlers 
SET division = 'NC High School Girls' 
WHERE division IN ('Girls', 'North Carolina Girls', 'High School Girls');

-- Step 5: Verification - show final state
SELECT 'DEPLOYMENT READY' as status, 
       division, 
       COUNT(*) as weight_classes, 
       MIN(max_weight) as min_weight, 
       MAX(max_weight) as max_weight
FROM weightClasses 
WHERE active = TRUE 
GROUP BY division 
ORDER BY division; 