# DeepEval Dashboard Server

This directory contains scripts to manage the DeepEval dashboard server in a production environment. The dashboard provides a web interface to view and analyze your evaluation results.

## Features

- Production-ready server management
- Automatic handling of existing server instances
- Cross-platform support (Linux, macOS, Windows)
- Graceful shutdown handling
- Proper logging
- Virtual environment management
- Dependency checking

## Requirements

- Python 3.8 or higher
- psutil package (automatically installed by the scripts)
- UV package manager (recommended) or pip

## Directory Structure

```
dashboard/
├── server.py          # Main server management script
├── run_server.sh      # Unix/macOS launcher script
├── run_server.bat     # Windows launcher script
└── README.md         # This file
```

## Usage

### On Unix-like Systems (Linux, macOS)

```bash
# Make the script executable
chmod +x run_server.sh

# Run the server
./run_server.sh
```

### On Windows

```batch
# Run the server
run_server.bat
```

The server will:
1. Check for Python and required dependencies
2. Set up/activate a virtual environment if needed
3. Stop any existing dashboard instances
4. Start a new dashboard server
5. Open the dashboard in your default browser

## Configuration

The server uses the following default settings:
- Port: 8501
- Host: localhost
- Results Directory: `.deepeval_results` in your project root

You can customize these settings by:
1. Setting environment variables:
   - `DEEPEVAL_RESULTS_DIR`: Custom results directory
   - `STREAMLIT_SERVER_PORT`: Custom port number

2. Modifying the scripts directly

## Logging

The server logs important events to the console, including:
- Server start/stop events
- Error conditions
- Port conflicts
- Process management

## Production Deployment

For production deployment:

1. Use a process manager like systemd, supervisor, or PM2
2. Set up proper monitoring
3. Configure logging to a file
4. Set up proper security measures (firewall rules, etc.)

Example systemd service file:

```ini
[Unit]
Description=DeepEval Dashboard
After=network.target

[Service]
Type=simple
User=deepeval
WorkingDirectory=/path/to/deepeval
ExecStart=/path/to/deepeval/examples/dashboard/run_server.sh
Restart=always
Environment=STREAMLIT_SERVER_PORT=8501
Environment=STREAMLIT_SERVER_ADDRESS=localhost

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

1. **Port already in use**
   - The server will automatically attempt to stop any existing instances
   - If the port is still blocked, check for other processes using: `lsof -i :8501`

2. **Virtual Environment Issues**
   - Delete the `.venv` directory and let the script recreate it
   - Ensure you have write permissions in the project directory

3. **Permission Issues**
   - Ensure the scripts are executable
   - Check file and directory permissions

## Security Considerations

1. The server runs on localhost by default for security
2. For remote access, set up a proper reverse proxy (nginx, Apache)
3. Implement authentication if needed
4. Keep Python and all dependencies updated
5. Follow security best practices for production deployment 