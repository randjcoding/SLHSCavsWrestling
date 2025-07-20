-- =====================================================
-- IMMEDIATE FIX FOR WRESTLER CREATION ERRORS
-- =====================================================
-- Run this RIGHT NOW to fix the constraint violations

-- Step 1: Remove problematic constraints
ALTER TABLE wrestlers DROP CONSTRAINT IF EXISTS wrestlers_division_check;
ALTER TABLE weightClasses DROP CONSTRAINT IF EXISTS weightclasses_division_check;

-- Step 2: Update existing data to consistent format
UPDATE weightClasses SET division = 'NC High School Boys' WHERE division IN ('Boys', 'North Carolina Boys');
UPDATE weightClasses SET division = 'NC High School Girls' WHERE division IN ('Girls', 'North Carolina Girls');
UPDATE wrestlers SET division = 'NC High School Boys' WHERE division IN ('Boys', 'North Carolina Boys');
UPDATE wrestlers SET division = 'NC High School Girls' WHERE division IN ('Girls', 'North Carolina Girls');

-- Step 3: Add flexible constraints (non-empty but no value restrictions)
ALTER TABLE weightClasses ADD CONSTRAINT weightclasses_division_not_empty CHECK (division IS NOT NULL AND division != '');
ALTER TABLE wrestlers ADD CONSTRAINT wrestlers_division_not_empty CHECK (division IS NOT NULL AND division != '');

-- Step 4: Verify current weight classes exist
SELECT 'Current Weight Classes' as info, division, COUNT(*) as count 
FROM weightClasses 
WHERE active = TRUE 
GROUP BY division 
ORDER BY division;

-- Step 5: If no weight classes exist, create basic ones
INSERT INTO weightClasses (weight_limit, division, level, description, active) 
SELECT * FROM (VALUES 
    (106, 'NC High School Boys', 'Varsity', '106 lbs - NC High School Boys', true),
    (113, 'NC High School Boys', 'Varsity', '113 lbs - NC High School Boys', true),
    (120, 'NC High School Boys', 'Varsity', '120 lbs - NC High School Boys', true),
    (126, 'NC High School Boys', 'Varsity', '126 lbs - NC High School Boys', true),
    (132, 'NC High School Boys', 'Varsity', '132 lbs - NC High School Boys', true),
    (138, 'NC High School Boys', 'Varsity', '138 lbs - NC High School Boys', true),
    (144, 'NC High School Boys', 'Varsity', '144 lbs - NC High School Boys', true),
    (150, 'NC High School Boys', 'Varsity', '150 lbs - NC High School Boys', true),
    (157, 'NC High School Boys', 'Varsity', '157 lbs - NC High School Boys', true),
    (165, 'NC High School Boys', 'Varsity', '165 lbs - NC High School Boys', true),
    (175, 'NC High School Boys', 'Varsity', '175 lbs - NC High School Boys', true),
    (190, 'NC High School Boys', 'Varsity', '190 lbs - NC High School Boys', true),
    (215, 'NC High School Boys', 'Varsity', '215 lbs - NC High School Boys', true),
    (285, 'NC High School Boys', 'Varsity', '285 lbs - NC High School Boys', true),
    
    (100, 'NC High School Girls', 'Varsity', '100 lbs - NC High School Girls', true),
    (105, 'NC High School Girls', 'Varsity', '105 lbs - NC High School Girls', true),
    (110, 'NC High School Girls', 'Varsity', '110 lbs - NC High School Girls', true),
    (115, 'NC High School Girls', 'Varsity', '115 lbs - NC High School Girls', true),
    (120, 'NC High School Girls', 'Varsity', '120 lbs - NC High School Girls', true),
    (125, 'NC High School Girls', 'Varsity', '125 lbs - NC High School Girls', true),
    (130, 'NC High School Girls', 'Varsity', '130 lbs - NC High School Girls', true),
    (135, 'NC High School Girls', 'Varsity', '135 lbs - NC High School Girls', true),
    (140, 'NC High School Girls', 'Varsity', '140 lbs - NC High School Girls', true),
    (145, 'NC High School Girls', 'Varsity', '145 lbs - NC High School Girls', true),
    (155, 'NC High School Girls', 'Varsity', '155 lbs - NC High School Girls', true),
    (170, 'NC High School Girls', 'Varsity', '170 lbs - NC High School Girls', true),
    (190, 'NC High School Girls', 'Varsity', '190 lbs - NC High School Girls', true),
    (200, 'NC High School Girls', 'Varsity', '200 lbs - NC High School Girls', true)
) AS v(weight_limit, division, level, description, active)
WHERE NOT EXISTS (
    SELECT 1 FROM weightClasses WHERE division = v.division AND weight_limit = v.weight_limit
);

-- Step 6: Verification - show what's available now
SELECT 'READY TO USE' as status, division, COUNT(*) as weight_classes, MIN(weight_limit) as min_weight, MAX(weight_limit) as max_weight
FROM weightClasses 
WHERE active = TRUE 
GROUP BY division 
ORDER BY division; 