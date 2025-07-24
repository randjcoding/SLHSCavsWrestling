#!/bin/bash

# =====================================================
# DOMAIN SETUP SCRIPT - slhscavswrestling.com
# =====================================================
# This script sets up nginx reverse proxy for your domain
# Run this AFTER setting up DNS at GoDaddy
# =====================================================

set -e  # Exit on any error

echo "🤼 Setting up slhscavswrestling.com domain..."
echo "=============================================="

# Get server IP for display
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || wget -qO- ifconfig.me 2>/dev/null || echo "Unable to detect")
echo "📍 Your server IP is: $SERVER_IP"
echo ""

# Step 1: Install nginx
echo "📦 Installing nginx..."
apt update
apt install nginx -y

# Step 2: Stop nginx to configure it
echo "⏹️  Stopping nginx for configuration..."
systemctl stop nginx

# Step 3: Create nginx configuration for your domain
echo "⚙️  Creating nginx configuration..."
tee /etc/nginx/sites-available/slhscavswrestling.com > /dev/null << 'EOF'
server {
    listen 80;
    server_name slhscavswrestling.com www.slhscavswrestling.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Log files
    access_log /var/log/nginx/slhscavswrestling.com.access.log;
    error_log /var/log/nginx/slhscavswrestling.com.error.log;

    # Main proxy to your Flask app
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if you add them later)
    location /static/ {
        alias /var/www/SLHSCavsWrestling/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
}
EOF

# Step 4: Enable the site
echo "🔗 Enabling the site..."
ln -sf /etc/nginx/sites-available/slhscavswrestling.com /etc/nginx/sites-enabled/

# Step 5: Remove default nginx site
echo "🗑️  Removing default nginx site..."
rm -f /etc/nginx/sites-enabled/default

# Step 6: Test nginx configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid!"
else
    echo "❌ Nginx configuration has errors!"
    exit 1
fi

# Step 7: Update your Flask app settings for production
echo "⚙️  Updating Flask app settings..."
cd /var/www/SLHSCavsWrestling

# Create/update .env file
tee .env > /dev/null << EOF
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://wrestling_app:SLHSWrestling2025!@localhost/slhs_wrestling
ADMIN_LOGIN_ROUTE=cavaliers-wrestling-admin-portal-2025
EOF

echo "✅ Updated .env file with production settings"

# Step 8: Update firewall
echo "🔥 Configuring firewall..."
ufw allow 80/tcp
ufw allow 443/tcp
echo "✅ Opened ports 80 (HTTP) and 443 (HTTPS)"

# Step 9: Start and enable services
echo "🚀 Starting services..."
systemctl start nginx
systemctl enable nginx
systemctl restart slhs-wrestling

# Step 10: Check service status
echo ""
echo "📊 Checking service status..."
echo "Nginx status:"
systemctl is-active nginx
echo "Flask app status:"
systemctl is-active slhs-wrestling

# Step 11: Test local connections
echo ""
echo "🧪 Testing local connections..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    echo "✅ Flask app responding on localhost"
else
    echo "⚠️  Flask app not responding on localhost"
fi

if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80 | grep -q "200"; then
    echo "✅ Nginx responding on port 80"
else
    echo "⚠️  Nginx not responding on port 80"
fi

# Final instructions
echo ""
echo "🎉 DOMAIN SETUP COMPLETE!"
echo "=========================="
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to GoDaddy and set up DNS (see instructions below)"
echo "2. Wait 5-10 minutes for DNS to propagate"
echo "3. Test your domain: http://slhscavswrestling.com"
echo ""
echo "🌐 GODADDY DNS SETUP:"
echo "====================="
echo "1. Log into GoDaddy.com"
echo "2. Go to 'My Products' → 'Domains'"
echo "3. Click 'Manage' next to slhscavswrestling.com"
echo "4. Click 'DNS' in the left sidebar"
echo "5. Add these records:"
echo ""
echo "   Record 1:"
echo "   Type: A"
echo "   Name: @ (or leave blank)"
echo "   Value: $SERVER_IP"
echo "   TTL: 600"
echo ""
echo "   Record 2:"
echo "   Type: A"
echo "   Name: www"
echo "   Value: $SERVER_IP"
echo "   TTL: 600"
echo ""
echo "💡 HELPFUL COMMANDS:"
echo "==================="
echo "Check nginx status:     systemctl status nginx"
echo "Check app status:       systemctl status slhs-wrestling"
echo "View nginx logs:        tail -f /var/log/nginx/slhscavswrestling.com.access.log"
echo "View app logs:          journalctl -u slhs-wrestling -f"
echo "Restart everything:     systemctl restart nginx slhs-wrestling"
echo ""
echo "🔍 TEST YOUR DOMAIN:"
echo "==================="
echo "After DNS setup, test these URLs:"
echo "http://slhscavswrestling.com"
echo "http://www.slhscavswrestling.com"
echo ""
echo "✅ Your wrestling website is ready to go! 🤼‍♂️" 