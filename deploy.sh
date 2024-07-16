#!/bin/bash

echo "Deleting old app"
sudo rm -rf /var/www/wendy-bot

echo "Creating app folder"
sudo mkdir -p /var/www/wendy-bot

echo "Moving files to app folder"
sudo cp -r . /var/www/wendy-bot

cd /var/www/wendy-bot

# Create and move the .env file
sudo mv env .env

# Update system packages
sudo apt-get update

echo "Installing python and pip"
sudo apt-get install -y python3 python3-pip python3-venv

# Create virtual environment
echo "Creating virtual environment"
sudo python3 -m venv /var/www/wendy-bot/venv
sudo chown -R $USER:$USER /var/www/wendy-bot/venv

# Activate virtual environment and install dependencies
echo "Installing application dependencies"
source /var/www/wendy-bot/venv/bin/activate
pip install -r requirements.txt

# Update and install Nginx if not already installed
if ! command -v nginx > /dev/null; then
    echo "Installing Nginx"
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Configure Nginx to act as a reverse proxy if not already configured
if [ ! -f /etc/nginx/sites-available/myapp ]; then
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo bash -c 'cat > /etc/nginx/sites-available/myapp <<EOF
server {
    listen 80;
    server_name 3.89.191.113;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/wendy-bot/myapp.sock;
    }
}
EOF'

    sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled
    sudo systemctl restart nginx
else
    echo "Nginx reverse proxy configuration already exists."
fi

# Stop any existing Gunicorn process
sudo pkill gunicorn || true
sudo rm -rf /var/www/wendy-bot/myapp.sock

# Start Gunicorn with the Flask application
echo "Starting Gunicorn"
sudo /var/www/wendy-bot/venv/bin/gunicorn --workers 3 --bind unix:/var/www/wendy-bot/myapp.sock app:app --user www-data --group www-data --daemon
echo "Started Gunicorn 🚀"
