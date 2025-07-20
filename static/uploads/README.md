# Southern Lee Wrestling - Uploads Folder

## 📂 **Purpose**

This folder stores user-uploaded files from the wrestling roster system.

## 📁 **Folder Structure**

```
uploads/
├── wrestlers/           # Wrestler profile photos
│   ├── 2025/           # Current school year
│   └── 2024/           # Previous years
├── staff/              # Staff/coach photos
│   ├── 2025/
│   └── 2024/
├── documents/          # PDF documents, forms
│   ├── rosters/        # Team rosters
│   ├── schedules/      # Match schedules
│   └── forms/          # Permission forms, etc.
└── temp/               # Temporary upload processing
```

## 🔧 **Technical Details**

### **File Handling**

- **Max File Size**: 10MB per file
- **Allowed Types**: JPG, JPEG, PNG, PDF, DOC, DOCX
- **Naming**: Auto-generated unique filenames
- **Processing**: Automatic image resizing/optimization

### **Security**

- **File Validation**: All uploads validated for type and content
- **Virus Scanning**: Files scanned before storage
- **Access Control**: Only authenticated users can upload
- **Path Security**: Secure file paths prevent directory traversal

### **Storage Management**

- **Cleanup**: Temporary files auto-deleted after 24 hours
- **Backup**: Regular backups of upload directory
- **Monitoring**: File system usage monitored
- **Compression**: Images automatically optimized

## 🛡️ **Security Measures**

1. **File Type Validation**: Only allowed file types accepted
2. **Size Limits**: Prevents large file attacks
3. **Content Scanning**: Files scanned for malicious content
4. **Secure Storage**: Files stored outside web root when possible
5. **Access Logs**: All upload activity logged

## 📋 **Usage Guidelines**

### **For Administrators**

- Upload wrestler/staff photos through admin interface
- Monitor disk usage regularly
- Review upload logs for suspicious activity
- Maintain backup schedule

### **For Users**

- Use appropriate file sizes (< 5MB recommended)
- Upload high-quality images for best results
- Follow naming conventions when possible
- Don't upload copyrighted material without permission

## ⚙️ **Configuration**

```python
# Flask configuration
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}
```

## 🗑️ **Cleanup Schedule**

- **Temporary files**: Deleted after 24 hours
- **Unused files**: Quarterly cleanup of orphaned files
- **Old seasons**: Archived after 3 years
- **Logs**: Upload logs rotated monthly

---

**⚠️ Important**: This folder is automatically managed by the application. Manual changes may cause issues.
