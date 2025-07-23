#!/bin/bash
# SLHS Wrestling Production Deployment Script
# Run this on your Digital Ocean droplet

set -e  # Exit on any error

echo "🤼 Starting SLHS Wrestling Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (sudo ./deploy.sh)"
    exit 1
fi

# Project directory
PROJECT_DIR="/var/www/SLHSCavsWrestling"
LOG_DIR="/var/log/slhs-wrestling"

print_info "Project directory: $PROJECT_DIR"

# Create log directory
print_info "Creating log directory..."
mkdir -p $LOG_DIR
chown root:root $LOG_DIR
print_status "Log directory created"

# Navigate to project directory
cd $PROJECT_DIR

# Activate virtual environment and install dependencies
print_info "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_status "Dependencies installed"

# Copy service file
print_info "Installing systemd service..."
cp slhs-wrestling.service /etc/systemd/system/
systemctl daemon-reload
print_status "Service installed"

# Enable and start service
print_info "Starting SLHS Wrestling service..."
systemctl enable slhs-wrestling
systemctl restart slhs-wrestling

# Wait a moment for service to start
sleep 3

# Check service status
if systemctl is-active --quiet slhs-wrestling; then
    print_status "SLHS Wrestling service is running!"
    print_info "Service status:"
    systemctl status slhs-wrestling --no-pager -l
else
    print_error "Service failed to start!"
    print_info "Checking logs..."
    journalctl -u slhs-wrestling --no-pager -l
    exit 1
fi

# Test the website
print_info "Testing website..."
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    print_status "Website is responding!"
else
    print_warning "Website might not be responding on localhost:5000"
fi

echo ""
print_status "🎉 Deployment completed successfully!"
print_info "Your website should now be running persistently at:"
print_info "   http://174.138.63.54:5000"
print_info ""
print_info "Useful commands:"
print_info "   sudo systemctl status slhs-wrestling    # Check status"
print_info "   sudo systemctl restart slhs-wrestling   # Restart service"
print_info "   sudo journalctl -u slhs-wrestling -f    # View logs"
print_info "   sudo systemctl stop slhs-wrestling      # Stop service" 