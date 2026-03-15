#!/bin/bash
echo "Pulling latest changes..."
git pull

echo "Rebuilding dashboard..."
cd dashboard
npm run build
sudo cp -r dist/* /var/www/html/
cd ..

echo "Restarting Docker services..."
docker compose down
docker compose up --build -d

echo "Deploy complete!"
