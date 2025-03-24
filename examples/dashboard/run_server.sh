#!/bin/bash

# Navigate to project root
cd "$(dirname "$0")/../.." || exit 1

# Check if Streamlit is already running
PORT=8501
EXISTING_PID=$(ps aux | grep "streamlit run" | grep -v grep | awk '{print $2}')

if [ ! -z "$EXISTING_PID" ]; then
    echo "Streamlit is already running on process $EXISTING_PID"
    read -p "Do you want to terminate it? (y/N) " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Terminating Streamlit process..."
        kill $EXISTING_PID
        sleep 2
    else
        echo "Exiting..."
        exit 1
    fi
fi

# Create results directory
mkdir -p .deepeval_results

# Run the app
if command -v uv >/dev/null 2>&1; then
    uv run -m streamlit run deepeval/dashboard/app.py
else
    python3 -m streamlit run deepeval/dashboard/app.py
fi 