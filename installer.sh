#!/bin/bash
# NebulAI Mining Suite Installer
# Quick setup script for Unix/Linux/MacOS

echo "================================================"
echo "    NebulAI Mining Suite Installer v1.0"
echo "================================================"
echo ""
echo "⚠️  WARNING: This software violates NebulAI ToS!"
echo "⚠️  Use at your own risk!"
echo ""
echo "Press Ctrl+C to cancel, or any key to continue..."
read -n 1 -s

# Check Python version
echo ""
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create necessary files
echo ""
echo "📄 Setting up configuration files..."

# Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "✅ Created .env file from template"
        echo "⚠️  Please edit .env and add your SOLANA_PRIVATE_KEY"
    else
        cat > .env << EOF
# NebulAI Mining Script Environment Variables
SOLANA_PRIVATE_KEY=your_solana_private_key_here
LOG_LEVEL=INFO
TOKEN_REFRESH_HOURS=23
EOF
        echo "✅ Created .env file"
        echo "⚠️  Please edit .env and add your SOLANA_PRIVATE_KEY"
    fi
else
    echo "✅ .env file already exists"
fi

# Create tokens.txt if it doesn't exist
if [ ! -f "tokens.txt" ]; then
    touch tokens.txt
    echo "✅ Created empty tokens.txt"
    echo "⚠️  Please add your JWT tokens to tokens.txt (one per line)"
else
    echo "✅ tokens.txt already exists"
fi

# Set secure permissions
echo ""
echo "🔒 Setting secure file permissions..."
chmod 600 .env
chmod 600 tokens.txt
echo "✅ File permissions secured"

# Create convenience scripts
echo ""
echo "🚀 Creating launcher scripts..."

# Create run script
cat > run_miner.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python nebulai_miner.py
EOF
chmod +x run_miner.sh

# Create monitor script
cat > run_monitor.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python monitor.py
EOF
chmod +x run_monitor.sh

# Create health check script
cat > run_health_check.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python health_check.py
EOF
chmod +x run_health_check.sh

echo "✅ Launcher scripts created"

# Run health check
echo ""
echo "🏥 Running health check..."
python health_check.py

# Final instructions
echo ""
echo "================================================"
echo "            Installation Complete!"
echo "================================================"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Edit .env file and add your Solana private key:"
echo "   nano .env"
echo ""
echo "2. Add your JWT tokens to tokens.txt:"
echo "   nano tokens.txt"
echo ""
echo "3. Run the health check:"
echo "   ./run_health_check.sh"
echo ""
echo "4. Start mining:"
echo "   ./run_miner.sh"
echo ""
echo "5. Monitor performance (in another terminal):"
echo "   ./run_monitor.sh"
echo ""
echo "================================================"
echo ""
echo "⚠️  Remember: This violates NebulAI's ToS!"
echo "⚠️  Your account may be suspended!"
echo ""