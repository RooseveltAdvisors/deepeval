#!/usr/bin/env python3
"""
DeepEval Dashboard Server
A production-ready server manager for the DeepEval dashboard.
"""
import os
import sys
import signal
import psutil
import socket
import webbrowser
import time
from pathlib import Path
import streamlit.web.bootstrap
from streamlit.web.server import Server
import logging
from typing import Optional, NoReturn, Tuple
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.getcwd(), '.deepeval_results', 'dashboard.log'))
    ]
)
logger = logging.getLogger('deepeval.dashboard')

class PortInUseError(Exception):
    """Raised when a port is already in use and user declines to kill the process."""
    pass

class ServerManager:
    """Manages the lifecycle of the Streamlit dashboard server."""
    
    def __init__(self, dashboard_path: str, port: int = 8501):
        """Initialize the server manager.
        
        Args:
            dashboard_path: Path to the dashboard application
            port: Port number to use for the server
        """
        self.dashboard_path = Path(dashboard_path).resolve()
        self.port = port
        self.current_port = None
        
        # Ensure dashboard exists
        if not self.dashboard_path.exists():
            raise FileNotFoundError(f"Dashboard file not found: {self.dashboard_path}")
            
        # Create results directory if it doesn't exist
        results_dir = Path(os.getcwd()) / '.deepeval_results'
        results_dir.mkdir(exist_ok=True)

    def is_port_in_use(self, port: int) -> Tuple[bool, Optional[psutil.Process]]:
        """Check if a port is in use and return the process if found.
        
        Args:
            port: Port number to check
            
        Returns:
            Tuple of (is_in_use, process_using_port)
        """
        # First check if port is open
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return False, None
                
        # If port is in use, try to find the process
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if ('streamlit' in cmdline and f'--server.port={port}' in cmdline) or \
                       (any(conn.laddr.port == port for conn in proc.connections())):
                        return True, proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return True, None

    def prompt_kill_process(self, proc: Optional[psutil.Process], port: int) -> bool:
        """Ask user for permission to kill the process using the port.
        
        Args:
            proc: Process to kill (if found)
            port: Port number in use
            
        Returns:
            bool: Whether the user agreed to kill the process
        """
        if proc:
            try:
                proc_name = proc.name()
                proc_cmdline = ' '.join(proc.cmdline())
                print(f"\nPort {port} is in use by process:")
                print(f"  PID: {proc.pid}")
                print(f"  Name: {proc_name}")
                print(f"  Command: {proc_cmdline}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"\nPort {port} is in use by an unknown process")
        else:
            print(f"\nPort {port} is in use but the process could not be identified")
            
        while True:
            response = input("\nWould you like to kill the process and start the server? [y/N] ").lower()
            if response in ('y', 'yes', 'n', 'no', ''):
                return response in ('y', 'yes')
            print("Please answer 'y' or 'n'")

    def stop_server(self, port: int, force: bool = False) -> bool:
        """Stop any running Streamlit server on the specified port.
        
        Args:
            port: Port number to free
            force: Whether to kill without asking (for cleanup)
            
        Returns:
            bool: Whether the port was successfully freed
        """
        in_use, proc = self.is_port_in_use(port)
        if not in_use:
            return True
            
        if not force and not self.prompt_kill_process(proc, port):
            return False
            
        if proc:
            logger.info(f"Stopping process on port {port} (PID: {proc.pid})")
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    logger.warning("Process did not terminate gracefully, forcing kill")
                    proc.kill()
                    proc.wait(timeout=5)
                logger.info(f"Successfully stopped process on port {port}")
                # Give the system a moment to free the port
                time.sleep(1)
                return not self.is_port_in_use(port)[0]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def start_server(self) -> NoReturn:
        """Start the Streamlit server."""
        # Check if port is in use
        if self.is_port_in_use(self.port)[0]:
            if not self.stop_server(self.port):
                raise PortInUseError(f"Port {self.port} is in use and permission to kill was denied")
            
        self.current_port = self.port
        logger.info(f"Starting server on port {self.port}")
        
        try:
            # Set environment variables
            os.environ.update({
                'STREAMLIT_SERVER_PORT': str(self.port),
                'STREAMLIT_SERVER_ADDRESS': 'localhost',
                'STREAMLIT_SERVER_HEADLESS': 'true',
                'STREAMLIT_SERVER_FILE_WATCHER_TYPE': 'watchdog',
                'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false'
            })

            # Configure Streamlit
            sys.argv = [
                "streamlit", "run",
                str(self.dashboard_path),
                "--server.port", str(self.port),
                "--server.address", "localhost",
                "--server.headless", "true",
                "--server.fileWatcherType", "watchdog",
                "--browser.gatherUsageStats", "false"
            ]
            
            # Open browser after short delay
            def open_browser():
                time.sleep(2)  # Wait for server to start
                webbrowser.open(f"http://localhost:{self.port}")
            
            import threading
            threading.Thread(target=open_browser, daemon=True).start()
            
            # Start server
            streamlit.web.bootstrap.run(
                str(self.dashboard_path),
                "",
                [],
                flag_options={}
            )
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            sys.exit(1)

    def cleanup(self) -> None:
        """Clean up resources before shutdown."""
        if self.current_port:
            self.stop_server(self.current_port, force=True)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DeepEval Dashboard Server")
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port number to use (default: 8501)"
    )
    return parser.parse_args()

def main() -> NoReturn:
    """Main entry point for the server management script."""
    args = parse_args()
    
    # Get dashboard path
    dashboard_path = Path(__file__).resolve().parent.parent.parent / "deepeval" / "dashboard" / "app.py"
    
    try:
        # Initialize server manager
        manager = ServerManager(
            dashboard_path=dashboard_path,
            port=args.port
        )
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, cleaning up...")
            manager.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start server
        manager.start_server()
    except PortInUseError as e:
        logger.error(str(e))
        print("\nPlease try again with a different port using the --port option")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 