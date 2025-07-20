-- =====================================================
-- UPDATE WEIGHT CLASSES TO "North Carolina Boys/Girls"
-- =====================================================
-- Run this SQL to update the division names and constraints
-- IMPORTANT: Run this BEFORE creating any wrestlers!

-- Step 1: Drop ALL existing constraints first
ALTER TABLE weightClasses DROP CONSTRAINT IF EXISTS weightclasses_division_check;
ALTER TABLE wrestlers DROP CONSTRAINT IF EXISTS wrestlers_division_check;

-- Step 2: Update existing data in weightClasses table
UPDATE weightClasses 
SET division = 'North Carolina Boys' 
WHERE division = 'Boys';

UPDATE weightClasses 
SET division = 'North Carolina Girls' 
WHERE division = 'Girls';

-- Step 3: Update existing data in wrestlers table (if any)
UPDATE wrestlers 
SET division = 'North Carolina Boys' 
WHERE division = 'Boys';

UPDATE wrestlers 
SET division = 'North Carolina Girls' 
WHERE division = 'Girls';

-- Step 4: Add the new constraints with updated values
ALTER TABLE weightClasses 
ADD CONSTRAINT weightclasses_division_check 
CHECK (division IN ('North Carolina Boys', 'North Carolina Girls'));

ALTER TABLE wrestlers 
ADD CONSTRAINT wrestlers_division_check 
CHECK (division IN ('North Carolina Boys', 'North Carolina Girls'));

-- Step 5: Also need to update the create wrestler form and app.py to use new division names
-- The Flask app needs to be updated to send the correct division values

-- Verification queries
SELECT 'weightClasses' as table_name, division, COUNT(*) as count 
FROM weightClasses GROUP BY division
UNION ALL
SELECT 'wrestlers' as table_name, division, COUNT(*) as count 
FROM wrestlers GROUP BY division; 