#!/usr/bin/env bash
# SIH26146: AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic
# Production Offline Deployment Launch Script

set -e

echo "======================================================================"
echo " Starting SIH26146 Bitcoin Monitoring & Investigation System"
echo " National Technical Research Organisation (NTRO)"
echo " Environment: Offline Linux Container Deployment"
echo "======================================================================"

# Step 1: Check Python and Docker dependencies
if command -v docker-compose &> /dev/null; then
    echo "[+] Docker Compose detected. Starting containerized offline environment..."
    docker-compose up --build -d
    echo "[✓] System running at http://localhost:8000"
    exit 0
fi

echo "[!] Docker Compose not detected. Falling back to local Virtual Environment execution..."

# Step 2: Virtual Environment fallback
if [ ! -d "venv" ]; then
    echo "[+] Creating local Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Step 3: Run pytest verification
echo "[+] Executing pre-flight integration tests..."
python -m pytest tests/test_pipeline.py -v

# Step 4: Launch FastAPI REST Server
echo "[+] Starting FastAPI Server on port 8000..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
