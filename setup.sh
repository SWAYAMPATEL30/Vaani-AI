#!/bin/bash
# Setup script for Voice Calling Agent

echo "🎤 Setting up Smart Voice Calling Agent..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✓ Python: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys!"
fi

# Create audio output directory
mkdir -p audio_output

# Initialize database
echo "Initializing database..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python app.py"
echo "3. Test: curl http://localhost:5000/health"
echo ""




