#!/bin/bash
# AWS EC2 Deployment Script

echo "🚀 Deploying to AWS EC2"

# Variables
EC2_IP="your-ec2-ip-address"
KEY_PATH="~/path/to/your-key.pem"

# Copy files to EC2
scp -i $KEY_PATH -r ./* ubuntu@$EC2_IP:~/app/

# SSH and deploy
ssh -i $KEY_PATH ubuntu@$EC2_IP << 'EOF'
    cd ~/app
    docker-compose down
    docker-compose pull
    docker-compose up -d --build
    echo "✅ Deployed successfully"
EOF

echo "📊 Access your app at: http://$EC2_IP:8000"