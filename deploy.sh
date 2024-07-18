#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

APP_DIR="/var/www/wendy-bot"

echo "Deleting old app"
sudo rm -rf $APP_DIR

echo "Creating app folder"
sudo mkdir -p $APP_DIR

echo "Moving files to app folder"
sudo cp -r . $APP_DIR

cd $APP_DIR

# Check and move the .env file
if [ -f "env" ]; then
    echo "Moving environment file"
    sudo mv env .env
else
    echo "Environment file not found, skipping move."
fi

# Update system packages
echo "Updating system packages"
sudo apt-get update

echo "Installing python and pip"
sudo apt-get install -y python3 python3-pip python3-venv

# Create virtual environment
echo "Creating virtual environment"
sudo python3 -m venv $APP_DIR/venv
sudo chown -R $USER:$USER $APP_DIR/venv

# Activate virtual environment and install dependencies
echo "Installing application dependencies"
source $APP_DIR/venv/bin/activate
pip install --upgrade pip  # Upgrade pip to the latest version
pip install -r requirements.txt

# Update and install Nginx if not already installed
if ! command -v nginx > /dev/null; then
    echo "Installing Nginx"
    sudo apt-get install -y nginx
fi

# Configure Nginx to act as a reverse proxy if not already configured
if [ ! -f /etc/nginx/sites-available/myapp ]; then
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo bash -c 'cat > /etc/nginx/sites-available/myapp <<EOF
server {
    listen 80;
    server_name wendy-ng.dev;

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/myapp.sock;
    }
}
EOF'

    sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled
    sudo nginx -t  # Test Nginx configuration
    sudo systemctl restart nginx
else
    echo "Nginx reverse proxy configuration already exists."
fi

# Stop any existing Gunicorn process
sudo pkill gunicorn || true
sudo rm -rf $APP_DIR/myapp.sock

# Start Gunicorn with the Flask application
# gunicorn --workers 3 --bind 0.0.0.0:8000 server:app &
echo "Starting Gunicorn"
sudo $APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/myapp.sock app:app --user www-data --group www-data --daemon
# sudo gunicorn --workers 3 --bind unix:myapp.sock  app:app --user www-data --group www-data --daemon
echo "Started Gunicorn 🚀"
