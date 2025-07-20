-- =====================================================
-- UPDATE STAFF ROLE CONSTRAINT TO INCLUDE WEBMASTER
-- =====================================================
-- Run this SQL to add the webmaster role to the staff table

-- Step 1: Drop the existing constraint
ALTER TABLE staff DROP CONSTRAINT IF EXISTS staff_role_check;

-- Step 2: Add the new constraint with webmaster included
ALTER TABLE staff 
ADD CONSTRAINT staff_role_check 
CHECK (role IN ('head_coach', 'assistant_coach', 'manager', 'medical', 'athletic_director', 'webmaster', 'volunteer'));

-- Verification query
SELECT role, COUNT(*) as count FROM staff GROUP BY role; 