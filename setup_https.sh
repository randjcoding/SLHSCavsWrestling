#!/bin/bash

# =====================================================
# HTTPS/SSL SETUP SCRIPT - slhscavswrestling.com
# =====================================================
# This script sets up HTTPS/SSL using Let's Encrypt
# Run this AFTER your domain is working on HTTP
# =====================================================

set -e  # Exit on any error

echo "🔒 Setting up HTTPS/SSL for slhscavswrestling.com..."
echo "=================================================="

# Check if domain is working first
echo "🧪 Testing if domain is working on HTTP..."
if curl -s -o /dev/null -w "%{http_code}" http://slhscavswrestling.com | grep -q "200"; then
    echo "✅ Domain is responding on HTTP"
else
    echo "❌ Domain is not responding on HTTP yet!"
    echo "Please wait for DNS propagation and make sure http://slhscavswrestling.com works first"
    exit 1
fi

# Step 1: Install snapd and certbot
echo "📦 Installing certbot..."
apt update
apt install snapd -y
snap install core; snap refresh core
snap install --classic certbot

# Create symlink for certbot command
ln -sf /snap/bin/certbot /usr/bin/certbot

# Step 2: Get SSL certificate
echo "🔒 Obtaining SSL certificate..."
echo "You'll be prompted for an email address for urgent renewal and security notices"
echo ""

# Stop nginx temporarily for standalone certificate generation
systemctl stop nginx

# Get certificate using standalone method
certbot certonly --standalone \
    --email admin@slhscavswrestling.com \
    --agree-tos \
    --no-eff-email \
    -d slhscavswrestling.com \
    -d www.slhscavswrestling.com

# Step 3: Update nginx configuration for HTTPS
echo "⚙️  Updating nginx configuration for HTTPS..."
tee /etc/nginx/sites-available/slhscavswrestling.com > /dev/null << 'EOF'
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name slhscavswrestling.com www.slhscavswrestling.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name slhscavswrestling.com www.slhscavswrestling.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/slhscavswrestling.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/slhscavswrestling.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
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
        proxy_set_header X-Forwarded-Proto https;
        
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

# Step 4: Test nginx configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid!"
else
    echo "❌ Nginx configuration has errors!"
    exit 1
fi

# Step 5: Start nginx
echo "🚀 Starting nginx with HTTPS..."
systemctl start nginx
systemctl reload nginx

# Step 6: Set up automatic renewal
echo "🔄 Setting up automatic SSL renewal..."
# Test renewal
certbot renew --dry-run

# Add renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

# Step 7: Update Flask app environment for HTTPS
echo "⚙️  Updating Flask app for HTTPS..."
cd /var/www/SLHSCavsWrestling

# Update .env file to prefer HTTPS
tee .env > /dev/null << EOF
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://wrestling_app:SLHSWrestling2025!@localhost/slhs_wrestling
ADMIN_LOGIN_ROUTE=cavaliers-wrestling-admin-portal-2025
PREFERRED_URL_SCHEME=https
EOF

# Restart Flask app
systemctl restart slhs-wrestling

# Step 8: Test HTTPS
echo ""
echo "🧪 Testing HTTPS connections..."
sleep 5

if curl -s -o /dev/null -w "%{http_code}" https://slhscavswrestling.com | grep -q "200"; then
    echo "✅ HTTPS is working for slhscavswrestling.com"
else
    echo "⚠️  HTTPS not responding for main domain"
fi

if curl -s -o /dev/null -w "%{http_code}" https://www.slhscavswrestling.com | grep -q "200"; then
    echo "✅ HTTPS is working for www.slhscavswrestling.com"
else
    echo "⚠️  HTTPS not responding for www subdomain"
fi

# Final status check
echo ""
echo "📊 Service Status:"
echo "Nginx: $(systemctl is-active nginx)"
echo "Flask App: $(systemctl is-active slhs-wrestling)"

echo ""
echo "🎉 HTTPS SETUP COMPLETE!"
echo "========================"
echo ""
echo "✅ Your website is now secure with HTTPS!"
echo "✅ HTTP automatically redirects to HTTPS"
echo "✅ SSL certificate will auto-renew"
echo ""
echo "🔍 TEST YOUR SECURE WEBSITE:"
echo "============================"
echo "https://slhscavswrestling.com"
echo "https://www.slhscavswrestling.com"
echo ""
echo "💡 HELPFUL COMMANDS:"
echo "==================="
echo "Check SSL cert:         certbot certificates"
echo "Test renewal:           certbot renew --dry-run"
echo "View nginx logs:        tail -f /var/log/nginx/slhscavswrestling.com.access.log"
echo "Check SSL rating:       https://www.ssllabs.com/ssltest/"
echo ""
echo "🔒 Your wrestling website is now professional and secure! 🤼‍♂️" 