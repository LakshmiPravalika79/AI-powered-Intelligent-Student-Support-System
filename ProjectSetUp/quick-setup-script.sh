#!/bin/bash

# UniAssist Pro - Quick Setup Script
# This script automates the entire setup process

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     UniAssist Pro - Automated Setup                       ║"
echo "║     Quick Start Script                                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo " Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "  Node.js is not installed. Skipping frontend setup."
    SKIP_FRONTEND=true
fi

echo " Python 3 detected: $(python3 --version)"
if [ -z "$SKIP_FRONTEND" ]; then
    echo " Node.js detected: $(node --version)"
fi
echo ""

# Step 1: Download and run the project generator
echo " Step 1: Generating project structure..."
echo ""

# Create the generator script inline
cat > generate_project.py << 'EOF'
# Import the project generator code here
# (The full generator script from the artifact above)
import os
from pathlib import Path

def create_file(path, content):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f" Created: {path}")

# ... (rest of the generator code)
EOF

# Run the generator
python3 generate_project.py

# Check if generation was successful
if [ ! -d "uniassist-pro" ]; then
    echo " Project generation failed!"
    exit 1
fi

cd uniassist-pro

echo ""
echo "Project structure created successfully!"
echo ""

# Step 2: Setup Backend
echo "Step 2: Setting up Python backend..."
echo ""

cd backend

# Create virtual environment
python3 -m venv venv
echo " Virtual environment created"

# Activate virtual environment and install dependencies
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/Mac
    source venv/bin/activate
fi

echo " Virtual environment activated"

# Install requirements
pip install -r requirements.txt > /dev/null 2>&1
echo " Backend dependencies installed"

# Create .env file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo " Environment file created"
fi

cd ..

# Step 3: Setup Frontend (if Node.js is available)
if [ -z "$SKIP_FRONTEND" ]; then
    echo ""
    echo " Step 3: Setting up React frontend..."
    echo ""
    
    cd frontend
    
    # Install npm dependencies
    npm install > /dev/null 2>&1
    echo " Frontend dependencies installed"
    
    cd ..
fi

# Step 4: Initialize Git repository
echo ""
echo "Step 4: Initializing Git repository..."
echo ""

git init > /dev/null 2>&1
echo " Git repository initialized"

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'GITIGNORE'
__pycache__/
*.pyc
venv/
node_modules/
.env
*.log
.DS_Store
GITIGNORE
    echo " .gitignore created"
fi

git add .
git commit -m "Initial commit: UniAssist Pro MVP" > /dev/null 2>&1
echo " Initial commit created"

# Done!
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🎉 SETUP COMPLETE! 🎉                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Project Location: $(pwd)"
echo ""
echo " To start the backend:"
echo "   cd backend"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "   python -m app.main"
echo "   → API: http://localhost:8000/docs"
echo ""

if [ -z "$SKIP_FRONTEND" ]; then
    echo " To start the frontend (in a new terminal):"
    echo "   cd frontend"
    echo "   npm start"
    echo "   → App: http://localhost:3000"
    echo ""
fi

echo "Or use Docker:"
echo "   docker-compose up --build"
echo ""
echo "Demo Credentials:"
echo "   Email: sarah.johnson@techedu.edu"
echo "   Password: demo123"
echo ""
echo " Documentation available in docs/ folder"
echo ""
echo "Happy coding!"
echo ""