#!/bin/bash
# setup.sh
# ─────────────────────────────────────────────────────────────────
# One-shot bootstrap script for AWS EC2 (Ubuntu 22.04)
# Installs Git + Docker and configures the Docker group.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Deepak8260/Two-tier-flask-mySQL-app/main/setup.sh | bash
# ─────────────────────────────────────────────────────────────────

set -e  # Exit immediately on any error

echo "──────────────────────────────────────────"
echo " FlaskBoard — EC2 Bootstrap Script"
echo "──────────────────────────────────────────"

echo ""
echo "[1/6] Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

echo ""
echo "[2/6] Installing Git..."
sudo apt install git -y
git --version

echo ""
echo "[3/6] Installing Docker..."
sudo apt install docker.io -y

echo ""
echo "[4/6] Starting and enabling Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

echo ""
echo "[5/6] Adding current user ($USER) to docker group..."
sudo usermod -aG docker $USER

echo ""
echo "[6/6] Verifying installation..."
docker --version

echo ""
echo "──────────────────────────────────────────"
echo " Setup completed successfully!"
echo ""
echo " IMPORTANT: Run the following command to"
echo " apply the docker group without logging out:"
echo ""
echo "   newgrp docker"
echo ""
echo " Then proceed to clone the repo:"
echo "   git clone https://github.com/Deepak8260/Two-tier-flask-mySQL-app.git"
echo "──────────────────────────────────────────"
