# 🚀 SOUTHERN LEE WRESTLING - DROPLET DEPLOYMENT

## 📋 **OVERVIEW**

This guide contains **everything needed** to deploy the wrestling roster system to the Digital Ocean droplet. All fixes for wrestler creation, weight class management, and UI enhancements.

---

## 🔧 **STEP 1: DATABASE SETUP ON DROPLET**

**Run `droplet_setup.sql` in the droplet's PostgreSQL:**

This SQL will:

- ✅ Insert basic NC High School weight classes (if none exist)
- ✅ Update division naming to be consistent
- ✅ Verify everything is ready for wrestler creation

---

## 📁 **STEP 2: FILES TO UPLOAD TO DROPLET**

### **Updated Application Files:**

```
app.py                              # Fixed database column references
templates/base.html                 # Added Font Awesome, static file links
templates/admin/create_wrestler.html # Fixed weight class display
templates/admin/create_weight_class.html # Fixed form fields
templates/admin/weight_classes.html  # Fixed table headers
templates/admin/dashboard.html       # Added weight class management
```

### **New Static Assets:**

```
static/css/custom.css               # Southern Lee styling
static/js/wrestling.js              # Enhanced functionality
static/images/README.md             # Image guidelines
static/uploads/README.md            # Upload documentation
```

---

## 🔗 **STEP 3: GIT WORKFLOW**

### **Local Preparation:**

```bash
# 1. Archive old files (run these commands in your terminal)
# (You'll do this manually - commands provided below)

# 2. Add changes to git
git add .

# 3. Commit with descriptive message
git commit -m "Wrestling roster system: Fixed database alignment, added static assets, enhanced UI

- Fixed database column naming (max_weight vs weight_limit)
- Added complete static folder structure with Southern Lee styling
- Enhanced wrestler creation with dynamic division filtering
- Added weight class management interface
- Improved admin dashboard with weight class navigation
- Added Font Awesome icons and responsive design
- Fixed all constraint issues for smooth wrestler creation"

# 4. Push to repository
git push origin main
```

### **Droplet Deployment:**

```bash
# SSH into your droplet
ssh your_user@174.138.63.54

# Navigate to app directory
cd /path/to/your/wrestling/app

# Pull latest changes
git pull origin main

# Run the database setup SQL
psql -d slhs_wrestling -f droplet_setup.sql

# Restart your Flask application (method depends on your setup)
# If using systemd:
sudo systemctl restart wrestling-app

# If running manually:
# pkill -f "python app.py"
# nohup python app.py > app.log 2>&1 &

# Verify it's working
curl http://localhost:5000
```

---

## 🧪 **STEP 4: TESTING ON DROPLET**

### **Test Wrestler Creation (Critical):**

1. Navigate to: `http://your-droplet-ip/cavaliers-wrestling-admin-portal-2025`
2. Login with admin credentials
3. Go to: Admin Dashboard → Manage Wrestlers → Add Wrestler
4. Test the process:
   - Select "NC High School Boys" division
   - Weight classes should appear dynamically
   - Fill required fields and submit
   - **Should work without errors!**

### **Test Weight Class Management:**

1. Go to: Admin Dashboard → **Manage Weight Classes** (new button)
2. Should see existing weight classes organized by division
3. Try creating a new weight class
4. Verify all functionality works

### **Test Static Assets:**

1. Check that Southern Lee styling loads correctly
2. Verify JavaScript functionality (dynamic filtering)
3. Test responsive design on different screen sizes

---

## 🚨 **TROUBLESHOOTING**

### **If Wrestler Creation Still Fails:**

```sql
-- Check if weight classes exist
SELECT division, COUNT(*) FROM weightClasses WHERE active = TRUE GROUP BY division;

-- Check for constraint issues
SELECT conname FROM pg_constraint WHERE conname LIKE '%division%';
```

### **If Static Files Don't Load:**

- Verify `static/` folder exists in app directory
- Check Flask is configured for static files
- Ensure file permissions are correct

### **If Git Issues:**

```bash
# If conflicts arise
git stash
git pull origin main
git stash pop
# Resolve any conflicts, then commit again
```

---

## ✅ **SUCCESS INDICATORS**

After successful deployment:

✅ **No database constraint errors**  
✅ **Wrestler creation works smoothly**  
✅ **Dynamic weight class filtering**  
✅ **Professional Southern Lee styling**  
✅ **Weight class management interface**  
✅ **Enhanced admin dashboard**  
✅ **All static assets loading**

---

## 📞 **DEPLOYMENT SUPPORT**

If issues arise during deployment:

1. **Check application logs** for error messages
2. **Verify database connection** and weight class data
3. **Test static file serving** and paths
4. **Review SQL execution** for any errors
5. **Check file permissions** on uploaded files

**The system is ready for production deployment!** 🤼‍♂️⚔️
