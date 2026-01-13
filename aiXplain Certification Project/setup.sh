#!/bin/bash
# Quick setup and run script for Policy Navigator Agent

set -e

echo "🚀 Policy Navigator Agent - Setup Script"
echo "========================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version installed"
echo ""

# Create virtual environment
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "⚙️  Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f "env_example.sh" ]; then
        cp env_example.sh .env
        echo "✅ Created .env from env_example.sh"
        echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
        echo "   - AIXPLAIN_API_KEY"
        echo "   - AIXPLAIN_TEAM_ID"
        echo "   - FEDERAL_REGISTER_API_KEY"
        echo "   - COURTLISTENER_API_KEY"
        echo "   - SLACK_WEBHOOK_URL (optional)"
    fi
else
    echo "⚠️  .env file already exists"
fi
echo ""

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/vector_store
mkdir -p logs
echo "✅ Data directories created"
echo ""

# Download datasets (optional)
echo "📥 Downloading policy datasets (this may take a few minutes)..."
read -p "Do you want to download datasets now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python download_datasets_script.py
    echo "✅ Datasets downloaded"
else
    echo "⏭️  Skipped dataset download. Run later with: python download_datasets_script.py"
fi
echo ""

# Build vector index
echo "🔨 Building vector index..."
read -p "Do you want to build the vector index now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python create_index_script.py
    echo "✅ Vector index built"
else
    echo "⏭️  Skipped index building. Run later with: python create_index_script.py"
fi
echo ""

# Final instructions
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Download datasets: python download_datasets_script.py"
echo "  3. Build vector index: python create_index_script.py"
echo "  4. Start web interface: streamlit run streamlit_app.py"
echo "  5. Access at http://localhost:8501"
echo ""
echo "For more information, see README.md"
