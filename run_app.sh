#!/bin/bash
# Census Employment Explorer - Easy Launcher
# Just double-click this file to start the app!

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Setting up for first time use..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -e ".[web]"
else
    source venv/bin/activate
fi

echo ""
echo "🚀 Starting Census Employment Explorer..."
echo "   Opening in your browser at http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop the app"
echo ""

streamlit run app.py --server.headless true
