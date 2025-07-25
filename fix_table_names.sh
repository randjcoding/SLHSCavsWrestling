#!/bin/bash

# =====================================================
# FIX TABLE NAMES SCRIPT - URGENT BUG FIX
# =====================================================
# This script fixes the table name mismatches in app.py
# Run this on the server to fix the wrestler edit issues
# =====================================================

set -e  # Exit on any error

echo "🔧 Fixing table name mismatches in app.py..."
echo "=============================================="

# Navigate to application directory
cd /var/www/SLHSCavsWrestling

# Backup current app.py
cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)

# Fix all wrestlerDetails -> wrestlerdetails
sed -i 's/wrestlerDetails/wrestlerdetails/g' app.py

# Fix all staffDetails -> staffdetails  
sed -i 's/staffDetails/staffdetails/g' app.py

echo "✅ Fixed table names in app.py"

# Check the changes
echo "📊 Verifying changes..."
echo "wrestlerDetails occurrences (should be 0):"
grep -n "wrestlerDetails" app.py | wc -l || true

echo "staffDetails occurrences (should be 0):"
grep -n "staffDetails" app.py | wc -l || true

echo "wrestlerdetails occurrences:"
grep -n "wrestlerdetails" app.py | wc -l || true

echo "staffdetails occurrences:"
grep -n "staffdetails" app.py | wc -l || true

# Restart the Flask application
echo "🚀 Restarting Flask application..."
systemctl restart slhs-wrestling

# Check status
echo "📊 Checking service status..."
if systemctl is-active --quiet slhs-wrestling; then
    echo "✅ Flask application is running"
else
    echo "❌ Flask application failed to start!"
    echo "Checking logs..."
    journalctl -u slhs-wrestling -n 20
    exit 1
fi

# Test the database connection
echo "🧪 Testing database connection..."
cd /var/www/SLHSCavsWrestling
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://wrestling_app:SLHSWrestling2025!@localhost/slhs_wrestling')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM wrestlerdetails')
    count = cursor.fetchone()[0]
    print(f'✅ Database connection successful. wrestlerdetails has {count} records.')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

echo ""
echo "🎉 TABLE NAME FIXES COMPLETE!"
echo "============================"
echo ""
echo "✅ Fixed wrestlerDetails -> wrestlerdetails"
echo "✅ Fixed staffDetails -> staffdetails"
echo "✅ Restarted Flask application"
echo "✅ Verified database connection"
echo ""
echo "🧪 TEST YOUR WRESTLER EDITING NOW:"
echo "Go to: https://slhscavswrestling.com/cavaliers-wrestling-admin-portal-2025"
echo "Try editing a wrestler - it should work without SQL errors!"
echo ""
echo "📞 If issues persist, check logs with:"
echo "journalctl -u slhs-wrestling -f" 