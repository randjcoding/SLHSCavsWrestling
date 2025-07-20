-- =====================================================
-- FLEXIBLE WEIGHT CLASS SYSTEM
-- =====================================================
-- This removes hardcoded constraints and makes divisions completely flexible

-- Step 1: Remove all division constraints to make it flexible
ALTER TABLE wrestlers DROP CONSTRAINT IF EXISTS wrestlers_division_check;
ALTER TABLE weightClasses DROP CONSTRAINT IF EXISTS weightclasses_division_check;

-- Step 2: Update existing data to new naming convention
UPDATE weightClasses 
SET division = 'NC High School Boys' 
WHERE division IN ('Boys', 'North Carolina Boys');

UPDATE weightClasses 
SET division = 'NC High School Girls' 
WHERE division IN ('Girls', 'North Carolina Girls');

UPDATE wrestlers 
SET division = 'NC High School Boys' 
WHERE division IN ('Boys', 'North Carolina Boys');

UPDATE wrestlers 
SET division = 'NC High School Girls' 
WHERE division IN ('Girls', 'North Carolina Girls');

-- Step 3: Add basic constraints (but not restrictive on division values)
ALTER TABLE weightClasses 
ADD CONSTRAINT weightclasses_division_not_empty 
CHECK (division IS NOT NULL AND division != '');

ALTER TABLE wrestlers 
ADD CONSTRAINT wrestlers_division_not_empty 
CHECK (division IS NOT NULL AND division != '');

-- Step 4: Add some sample additional divisions for demonstration
INSERT INTO weightClasses (weight_limit, division, level, description) VALUES
-- Middle School divisions
(80, 'NC Middle School Boys', 'JV', '80 lbs - Middle School Boys'),
(86, 'NC Middle School Boys', 'JV', '86 lbs - Middle School Boys'),
(92, 'NC Middle School Boys', 'JV', '92 lbs - Middle School Boys'),
(98, 'NC Middle School Boys', 'JV', '98 lbs - Middle School Boys'),
(104, 'NC Middle School Boys', 'JV', '104 lbs - Middle School Boys'),
(110, 'NC Middle School Boys', 'JV', '110 lbs - Middle School Boys'),
(116, 'NC Middle School Boys', 'JV', '116 lbs - Middle School Boys'),
(122, 'NC Middle School Boys', 'JV', '122 lbs - Middle School Boys'),
(128, 'NC Middle School Boys', 'JV', '128 lbs - Middle School Boys'),
(134, 'NC Middle School Boys', 'JV', '134 lbs - Middle School Boys'),
(140, 'NC Middle School Boys', 'JV', '140 lbs - Middle School Boys'),
(147, 'NC Middle School Boys', 'JV', '147 lbs - Middle School Boys'),
(155, 'NC Middle School Boys', 'JV', '155 lbs - Middle School Boys'),
(172, 'NC Middle School Boys', 'JV', '172 lbs - Middle School Boys'),
(190, 'NC Middle School Boys', 'JV', '190 lbs - Middle School Boys'),
(285, 'NC Middle School Boys', 'JV', '285 lbs - Middle School Boys'),

-- Middle School Girls
(88, 'NC Middle School Girls', 'JV', '88 lbs - Middle School Girls'),
(95, 'NC Middle School Girls', 'JV', '95 lbs - Middle School Girls'),
(101, 'NC Middle School Girls', 'JV', '101 lbs - Middle School Girls'),
(107, 'NC Middle School Girls', 'JV', '107 lbs - Middle School Girls'),
(113, 'NC Middle School Girls', 'JV', '113 lbs - Middle School Girls'),
(120, 'NC Middle School Girls', 'JV', '120 lbs - Middle School Girls'),
(126, 'NC Middle School Girls', 'JV', '126 lbs - Middle School Girls'),
(132, 'NC Middle School Girls', 'JV', '132 lbs - Middle School Girls'),
(138, 'NC Middle School Girls', 'JV', '138 lbs - Middle School Girls'),
(145, 'NC Middle School Girls', 'JV', '145 lbs - Middle School Girls'),
(152, 'NC Middle School Girls', 'JV', '152 lbs - Middle School Girls'),
(160, 'NC Middle School Girls', 'JV', '160 lbs - Middle School Girls'),
(170, 'NC Middle School Girls', 'JV', '170 lbs - Middle School Girls'),
(182, 'NC Middle School Girls', 'JV', '182 lbs - Middle School Girls'),
(200, 'NC Middle School Girls', 'JV', '200 lbs - Middle School Girls');

-- Step 5: Create index for faster division lookups
CREATE INDEX IF NOT EXISTS idx_weightclasses_division ON weightClasses(division);
CREATE INDEX IF NOT EXISTS idx_wrestlers_division ON wrestlers(division);

-- Verification: Show all available divisions
SELECT 
    division,
    COUNT(*) as weight_class_count,
    MIN(weight_limit) as min_weight,
    MAX(weight_limit) as max_weight
FROM weightClasses 
GROUP BY division 
ORDER BY division; 