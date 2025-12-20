#!/bin/bash

# UniAssist Pro - GitHub Repository Setup Script
# This script helps you push your project to GitHub

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     UniAssist Pro - GitHub Setup                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git first."
    exit 1
fi

# Check if gh (GitHub CLI) is installed
if command -v gh &> /dev/null; then
    USE_GH_CLI=true
    echo "GitHub CLI detected"
else
    USE_GH_CLI=false
    echo " GitHub CLI not found. Manual repository creation required."
fi

echo ""

# Get repository name
read -p "Enter repository name (default: uniassist-pro): " REPO_NAME
REPO_NAME=${REPO_NAME:-uniassist-pro}

# Get repository visibility
read -p "Make repository public or private? (public/private, default: private): " VISIBILITY
VISIBILITY=${VISIBILITY:-private}

# Get repository description
read -p "Enter repository description (optional): " DESCRIPTION
DESCRIPTION=${DESCRIPTION:-"AI-Powered Student Support System - DBIM MVP"}

echo ""
echo "Repository Configuration:"
echo "   Name: $REPO_NAME"
echo "   Visibility: $VISIBILITY"
echo "   Description: $DESCRIPTION"
echo ""

read -p "Proceed with setup? (y/n): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""

# Check if we're in the project directory
if [ ! -f "README.md" ]; then
    echo "Please run this script from the project root directory (uniassist-pro/)"
    exit 1
fi

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: UniAssist Pro MVP"
    echo "Git repository initialized and committed"
else
    echo "Git repository already initialized"
fi

echo ""

if [ "$USE_GH_CLI" = true ]; then
    # Use GitHub CLI to create repository
    echo " Creating GitHub repository using GitHub CLI..."
    
    if [ "$VISIBILITY" = "public" ]; then
        gh repo create "$REPO_NAME" --source=. --public --description "$DESCRIPTION" --push
    else
        gh repo create "$REPO_NAME" --source=. --private --description "$DESCRIPTION" --push
    fi
    
    if [ $? -eq 0 ]; then
        echo "Repository created and code pushed successfully!"
        echo ""
        echo "Repository URL: https://github.com/$(gh api user --jq .login)/$REPO_NAME"
    else
        echo "Failed to create repository with GitHub CLI"
        exit 1
    fi
else
    # Manual setup instructions
    echo "Manual Setup Instructions:"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository named: $REPO_NAME"
    echo "3. Choose visibility: $VISIBILITY"
    echo "4. Do NOT initialize with README, .gitignore, or license"
    echo "5. After creating, run these commands:"
    echo ""
    echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    
    read -p "Have you created the repository? Enter the repository URL: " REPO_URL
    
    if [ ! -z "$REPO_URL" ]; then
        echo ""
        echo "Adding remote and pushing..."
        
        git remote add origin "$REPO_URL"
        git branch -M main
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo "Code pushed successfully!"
            echo "Repository: $REPO_URL"
        else
            echo "Push failed. Please check the repository URL and try again."
        fi
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              GitHub Setup Complete!                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next Steps:"
echo "   1. Visit your repository on GitHub"
echo "   2. Set up GitHub Actions for CI/CD (already configured)"
echo "   3. Add collaborators if needed"
echo "   4. Enable GitHub Pages for documentation"
echo ""
echo "Recommended GitHub Settings:"
echo "   • Enable branch protection for 'main'"
echo "   • Require pull request reviews"
echo "   • Enable automatic security updates"
echo ""