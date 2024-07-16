#!/bin/bash

echo "deleting old app"
sudo rm -rf /var/www/wendy-bot

echo "creating app folder"
sudo mkdir -p /var/www/wendy-bot

echo "moving files to app folder"
sudo mv * /var/www/wendy-bot

# Navigate to the app directory
cd /var/www/wendy-bot
sudo mv env .env

# Ensure system packages are up to date
sudo apt-get update

# Install Python, pip, and venv if not already installed
echo "installing python and pip"
sudo apt-get install -y python3 python3-pip python3-venv

# Create and activate virtual environment
echo "creating virtual environment"
python3 -m venv venv
source venv/bin/activate

# Install application dependencies from requirements.txt
echo "installing application dependencies"
venv/bin/pip install -r requirements.txt

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
    server_name _;

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
echo "starting gunicorn"
sudo /var/www/wendy-bot/venv/bin/gunicorn --workers 3 --bind unix:/var/www/wendy-bot/myapp.sock app:app --user www-data --group www-data --daemon
echo "started gunicorn 🚀"
