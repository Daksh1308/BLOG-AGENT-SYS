#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Check .env
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Create it with:"
    echo '  OPENAI_API_KEY=sk-or-v1-...'
    exit 1
fi

# Install if needed
if ! command -v streamlit &>/dev/null; then
    echo "==> Installing dependencies..."
    pip install -r requirements.txt
fi

echo "==> Starting Streamlit on http://0.0.0.0:8501"
echo "    (accessible from other devices on your local network)"
exec streamlit run bwa_frontend.py --server.address 0.0.0.0 --server.port 8501
