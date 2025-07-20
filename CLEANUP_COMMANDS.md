# 📁 FILE CLEANUP COMMANDS

## 🗂️ **STEP-BY-STEP FILE ORGANIZATION**

**Run these commands one by one in your terminal:**

```bash
# Move all extra SQL files to archive
move FINAL_WORKING_FIX.sql archive\
move IMMEDIATE_FIX.sql archive\
move flexible_weight_classes.sql archive\
move weight_class_update.sql archive\
move staff_role_update.sql archive\
move roster_database_setup.sql archive\

# Move all extra MD files to archive (keep serverCreation.md)
move PRODUCTION_READY.md archive\
move production_changes_tracker.md archive\
move FIX_BUTTONS_AND_ERRORS.md archive\
move READY_TO_TEST.md archive\

# Move this cleanup file to archive too (after you're done with it)
move CLEANUP_COMMANDS.md archive\
```

## 📋 **FILES REMAINING IN ROOT:**

After cleanup, you should have:

```
SLHSCavsWrestling/
├── app.py                      # Main application
├── droplet_setup.sql          # ONLY SQL for droplet
├── DROPLET_DEPLOYMENT.md      # ONLY deployment guide
├── serverCreation.md           # Original documentation (keep)
├── README.md                   # Original readme (keep)
├── .gitignore                  # Updated to ignore archive/
├── templates/                  # All template files
├── static/                     # All static assets
├── venv/                       # Python environment
├── .git/                       # Git repository
└── archive/                    # All development files (ignored by git)
```

## ✅ **VERIFICATION**

After running the commands, verify:

- ✅ Only `droplet_setup.sql` remains in root
- ✅ Only `DROPLET_DEPLOYMENT.md` remains in root
- ✅ All other SQL/MD files moved to `archive/`
- ✅ `archive/` added to `.gitignore`

## 🚀 **READY FOR GIT**

Once cleanup is complete:

```bash
git add .
git commit -m "Wrestling roster system deployment ready"
git push origin main
```
