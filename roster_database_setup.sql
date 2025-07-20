-- =====================================================
-- SLHS Wrestling Roster Database Setup
-- =====================================================
-- Run this SQL in your local PostgreSQL database first
-- Then apply to production server after testing

-- =====================================================
-- 1. WEIGHT CLASSES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS weightClasses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    max_weight INTEGER NOT NULL,
    division VARCHAR(20) NOT NULL CHECK (division IN ('Boys', 'Girls')),
    level VARCHAR(20) NOT NULL DEFAULT 'Varsity' CHECK (level IN ('Varsity', 'JV')),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(max_weight, division, level)
);

-- Insert North Carolina High School Weight Classes
-- Men's Varsity Weight Classes
INSERT INTO weightClasses (name, max_weight, division, level) VALUES
('106 lbs', 106, 'Boys', 'Varsity'),
('113 lbs', 113, 'Boys', 'Varsity'),
('120 lbs', 120, 'Boys', 'Varsity'),
('126 lbs', 126, 'Boys', 'Varsity'),
('132 lbs', 132, 'Boys', 'Varsity'),
('138 lbs', 138, 'Boys', 'Varsity'),
('144 lbs', 144, 'Boys', 'Varsity'),
('150 lbs', 150, 'Boys', 'Varsity'),
('157 lbs', 157, 'Boys', 'Varsity'),
('165 lbs', 165, 'Boys', 'Varsity'),
('175 lbs', 175, 'Boys', 'Varsity'),
('190 lbs', 190, 'Boys', 'Varsity'),
('215 lbs', 215, 'Boys', 'Varsity'),
('285 lbs', 285, 'Boys', 'Varsity');

-- Women's Varsity Weight Classes
INSERT INTO weightClasses (name, max_weight, division, level) VALUES
('100 lbs', 100, 'Girls', 'Varsity'),
('107 lbs', 107, 'Girls', 'Varsity'),
('114 lbs', 114, 'Girls', 'Varsity'),
('120 lbs', 120, 'Girls', 'Varsity'),
('126 lbs', 126, 'Girls', 'Varsity'),
('132 lbs', 132, 'Girls', 'Varsity'),
('138 lbs', 138, 'Girls', 'Varsity'),
('145 lbs', 145, 'Girls', 'Varsity'),
('152 lbs', 152, 'Girls', 'Varsity'),
('165 lbs', 165, 'Girls', 'Varsity'),
('185 lbs', 185, 'Girls', 'Varsity'),
('235 lbs', 235, 'Girls', 'Varsity');

-- =====================================================
-- 2. SCHOOL YEARS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS years (
    id SERIAL PRIMARY KEY,
    school_year VARCHAR(20) NOT NULL UNIQUE, -- e.g., '2025-2026'
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL,
    is_current BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert current and future school years
INSERT INTO years (school_year, start_year, end_year, is_current) VALUES
('2025-2026', 2025, 2026, true),
('2024-2025', 2024, 2025, false),
('2023-2024', 2023, 2024, false);

-- =====================================================
-- 3. WRESTLERS TABLE (Main roster information)
-- =====================================================

CREATE TABLE IF NOT EXISTS wrestlers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    weight_class_id INTEGER REFERENCES weightClasses(id),
    division VARCHAR(20) NOT NULL CHECK (division IN ('Boys', 'Girls')),
    level VARCHAR(20) NOT NULL CHECK (level IN ('Varsity', 'JV')),
    rank_in_division INTEGER DEFAULT 1,
    grade INTEGER NOT NULL CHECK (grade >= 9 AND grade <= 12),
    email VARCHAR(255),
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    year_id INTEGER REFERENCES years(id),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(weight_class_id, rank_in_division, level, year_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_wrestlers_weight_class ON wrestlers(weight_class_id);
CREATE INDEX IF NOT EXISTS idx_wrestlers_year ON wrestlers(year_id);
CREATE INDEX IF NOT EXISTS idx_wrestlers_active ON wrestlers(active);

-- =====================================================
-- 4. WRESTLER DETAILS TABLE (Detailed biographical info)
-- =====================================================

CREATE TABLE IF NOT EXISTS wrestlerDetails (
    id SERIAL PRIMARY KEY,
    wrestler_id INTEGER UNIQUE REFERENCES wrestlers(id) ON DELETE CASCADE,
    biography TEXT,
    divisions_wrestled JSONB DEFAULT '[]'::jsonb, -- Array of divisions wrestled
    track_wrestling_id VARCHAR(50),
    track_wrestling_url VARCHAR(255),
    primary_photo_url VARCHAR(255),
    secondary_photo_url VARCHAR(255),
    primary_photo_id INTEGER,
    secondary_photo_id INTEGER,
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50) DEFAULT 'NC',
    zip_code VARCHAR(10),
    phone_number VARCHAR(20),
    role VARCHAR(50) DEFAULT 'wrestler' CHECK (role IN ('wrestler', 'captain', 'co-captain')),
    achievements JSONB DEFAULT '[]'::jsonb, -- Array of achievements/awards
    collegiate_aspirations TEXT,
    home_town VARCHAR(100),
    home_state VARCHAR(50) DEFAULT 'NC',
    show_in_modal JSONB DEFAULT '{"biography": true, "achievements": true, "collegiate_aspirations": true, "record": true}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 5. WRESTLER PHOTOS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS wrestlerPhotos (
    id SERIAL PRIMARY KEY,
    wrestler_id INTEGER REFERENCES wrestlers(id) ON DELETE CASCADE,
    photo_url VARCHAR(255) NOT NULL,
    photo_type VARCHAR(50) DEFAULT 'general' CHECK (photo_type IN ('primary', 'secondary', 'general', 'action', 'headshot')),
    caption TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wrestler_photos_wrestler ON wrestlerPhotos(wrestler_id);

-- =====================================================
-- 6. STAFF TABLE (Basic staff information)
-- =====================================================

CREATE TABLE IF NOT EXISTS staff (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('head_coach', 'assistant_coach', 'manager', 'medical', 'athletic_director', 'volunteer')),
    user_id INTEGER REFERENCES users(id),
    email VARCHAR(255),
    phone_number VARCHAR(20),
    year_id INTEGER REFERENCES years(id),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_staff_role ON staff(role);
CREATE INDEX IF NOT EXISTS idx_staff_year ON staff(year_id);

-- =====================================================
-- 7. STAFF DETAILS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS staffDetails (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER UNIQUE REFERENCES staff(id) ON DELETE CASCADE,
    biography TEXT,
    wrestling_history TEXT,
    years_coaching INTEGER DEFAULT 0,
    certifications JSONB DEFAULT '[]'::jsonb, -- Array of certifications
    achievements JSONB DEFAULT '[]'::jsonb, -- Array of coaching achievements
    education TEXT,
    specialties JSONB DEFAULT '[]'::jsonb, -- Array of coaching specialties
    show_in_modal JSONB DEFAULT '{"biography": true, "wrestling_history": true, "years_coaching": true, "achievements": true}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 8. STAFF PHOTOS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS staffPhotos (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER REFERENCES staff(id) ON DELETE CASCADE,
    photo_url VARCHAR(255) NOT NULL,
    photo_type VARCHAR(50) DEFAULT 'general' CHECK (photo_type IN ('primary', 'secondary', 'general', 'action', 'headshot')),
    caption TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_staff_photos_staff ON staffPhotos(staff_id);

-- =====================================================
-- GRANT PERMISSIONS TO wrestling_app USER
-- =====================================================

-- Grant permissions on all new tables
GRANT ALL PRIVILEGES ON TABLE weightClasses TO wrestling_app;
GRANT ALL PRIVILEGES ON TABLE years TO wrestling_app;
GRANT ALL PRIVILEGES ON TABLE wrestlers TO wrestling_app;
GRANT ALL PRIVILEGES ON TABLE wrestlerDetails TO wrestling_app;
GRANT ALL PRIVILEGES ON TABLE wrestlerPhotos TO wrestling_app;
GRANT ALL PRIVILEGES ON TABLE staff TO wrestling_app;
GRANT ALL PRIVILEGES ON TABLE staffDetails TO wrestling_app;
GRANT ALL PRIVILEGES ON TABLE staffPhotos TO wrestling_app;

-- Grant permissions on sequences
GRANT ALL PRIVILEGES ON SEQUENCE weightClasses_id_seq TO wrestling_app;
GRANT ALL PRIVILEGES ON SEQUENCE years_id_seq TO wrestling_app;
GRANT ALL PRIVILEGES ON SEQUENCE wrestlers_id_seq TO wrestling_app;
GRANT ALL PRIVILEGES ON SEQUENCE wrestlerDetails_id_seq TO wrestling_app;
GRANT ALL PRIVILEGES ON SEQUENCE wrestlerPhotos_id_seq TO wrestling_app;
GRANT ALL PRIVILEGES ON SEQUENCE staff_id_seq TO wrestling_app;
GRANT ALL PRIVILEGES ON SEQUENCE staffDetails_id_seq TO wrestling_app;
GRANT ALL PRIVILEGES ON SEQUENCE staffPhotos_id_seq TO wrestling_app;

-- =====================================================
-- SAMPLE DATA (Optional - for testing)
-- =====================================================

-- Insert a sample head coach
INSERT INTO staff (first_name, last_name, role, email, year_id) 
SELECT 'John', 'Smith', 'head_coach', 'coach.smith@southernlee.edu', id 
FROM years WHERE is_current = true;

-- Insert sample staff details
INSERT INTO staffDetails (staff_id, biography, wrestling_history, years_coaching, show_in_modal)
SELECT id, 'Experienced wrestling coach with a passion for developing young athletes.', 
       'Former state champion, collegiate wrestler at NC State', 15,
       '{"biography": true, "wrestling_history": true, "years_coaching": true}'::jsonb
FROM staff WHERE role = 'head_coach' LIMIT 1;

-- Insert a sample wrestler
INSERT INTO wrestlers (first_name, last_name, weight_class_id, division, level, grade, year_id)
SELECT 'Michael', 'Johnson', wc.id, 'Boys', 'Varsity', 11, y.id
FROM weightClasses wc, years y 
WHERE wc.max_weight = 150 AND wc.division = 'Boys' AND y.is_current = true
LIMIT 1;

-- Insert sample wrestler details
INSERT INTO wrestlerDetails (wrestler_id, biography, achievements, collegiate_aspirations, show_in_modal)
SELECT id, 'Dedicated wrestler with strong work ethic and team leadership qualities.',
       '["Regional Qualifier 2024", "Team Captain"]'::jsonb,
       'Plans to wrestle at the collegiate level, interested in NC State and UNC programs.',
       '{"biography": true, "achievements": true, "collegiate_aspirations": true, "record": true}'::jsonb
FROM wrestlers WHERE first_name = 'Michael' AND last_name = 'Johnson' LIMIT 1;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check all tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('weightclasses', 'years', 'wrestlers', 'wrestlerdetails', 'wrestlerphotos', 'staff', 'staffdetails', 'staffphotos')
ORDER BY table_name;

-- Check weight classes data
SELECT division, level, COUNT(*) as weight_class_count 
FROM weightClasses 
GROUP BY division, level 
ORDER BY division, level;

-- Check sample data
SELECT 
    w.first_name || ' ' || w.last_name as wrestler_name,
    wc.name as weight_class,
    w.division,
    w.level,
    w.grade
FROM wrestlers w
JOIN weightClasses wc ON w.weight_class_id = wc.id;

SELECT 
    s.first_name || ' ' || s.last_name as staff_name,
    s.role,
    sd.years_coaching
FROM staff s
LEFT JOIN staffDetails sd ON s.id = sd.staff_id; 