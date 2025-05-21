"""
Terminal handler for RA.Aid.

This module provides functionality to handle terminal input and output.
"""

import logging
import os
import pty
import select
import subprocess
import threading
from typing import Dict, Any, Optional, List, Callable

from ra_aid.server.broadcast_sender import get_broadcast_queue
from ra_aid.terminal.prompt_handler import capture_terminal_output, start_prompt_handler

# Create logger
logger = logging.getLogger(__name__)

# Global dictionary to store terminal processes
terminals: Dict[int, Dict[str, Any]] = {}

# Terminal ID counter
terminal_id_counter = 0


def get_next_terminal_id() -> int:
    """Get the next terminal ID."""
    global terminal_id_counter
    terminal_id_counter += 1
    return terminal_id_counter


def create_terminal(command: List[str], cwd: Optional[str] = None) -> int:
    """Create a new terminal process.
    
    Args:
        command: The command to run
        cwd: The working directory for the command
        
    Returns:
        The terminal ID
    """
    # Start the prompt handler if it's not already running
    start_prompt_handler()
    
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    # Start the process
    process = subprocess.Popen(
        command,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        cwd=cwd,
        env=os.environ.copy(),
        start_new_session=True,
        universal_newlines=True
    )
    
    # Close the slave end of the pty
    os.close(slave)
    
    # Get a terminal ID
    terminal_id = get_next_terminal_id()
    
    # Create a thread to read from the terminal
    thread = threading.Thread(
        target=_read_terminal,
        args=(terminal_id, master, process),
        daemon=True
    )
    thread.start()
    
    # Store the terminal information
    terminals[terminal_id] = {
        "id": terminal_id,
        "process": process,
        "master": master,
        "thread": thread,
        "command": command,
        "cwd": cwd,
        "running": True
    }
    
    logger.info(f"Created terminal {terminal_id} with command: {command}")
    
    return terminal_id


def _read_terminal(terminal_id: int, master: int, process: subprocess.Popen):
    """Read from the terminal and broadcast the output.
    
    Args:
        terminal_id: The terminal ID
        master: The master end of the pty
        process: The process object
    """
    # Get the broadcast queue
    broadcast_queue = get_broadcast_queue()
    
    # Buffer for terminal output
    output_buffer = ""
    
    # Read from the terminal until the process exits
    while terminals.get(terminal_id, {}).get("running", False):
        try:
            # Check if there's data to read
            r, _, _ = select.select([master], [], [], 0.1)
            
            if r:
                # Read from the terminal
                data = os.read(master, 1024).decode("utf-8", errors="replace")
                
                # Add to the buffer
                output_buffer += data
                
                # Check for prompts in the output
                capture_terminal_output(output_buffer)
                
                # Broadcast the output
                if broadcast_queue:
                    broadcast_queue.put({
                        "type": "terminal_output",
                        "payload": {
                            "terminal_id": terminal_id,
                            "output": data
                        }
                    })
                
                # Check if the process has exited
                if process.poll() is not None:
                    break
        except (OSError, IOError) as e:
            logger.error(f"Error reading from terminal {terminal_id}: {e}")
            break
    
    # Process has exited
    if terminal_id in terminals:
        terminals[terminal_id]["running"] = False
        
        # Broadcast the exit status
        if broadcast_queue:
            broadcast_queue.put({
                "type": "terminal_exit",
                "payload": {
                    "terminal_id": terminal_id,
                    "exit_code": process.returncode
                }
            })
        
        logger.info(f"Terminal {terminal_id} exited with code: {process.returncode}")


def write_to_terminal(terminal_id: int, data: str) -> bool:
    """Write data to a terminal.
    
    Args:
        terminal_id: The terminal ID
        data: The data to write
        
    Returns:
        True if the data was written, False otherwise
    """
    if terminal_id not in terminals:
        logger.warning(f"Terminal {terminal_id} not found")
        return False
    
    terminal = terminals[terminal_id]
    
    if not terminal["running"]:
        logger.warning(f"Terminal {terminal_id} is not running")
        return False
    
    try:
        # Write to the terminal
        os.write(terminal["master"], data.encode("utf-8"))
        return True
    except (OSError, IOError) as e:
        logger.error(f"Error writing to terminal {terminal_id}: {e}")
        return False


def kill_terminal(terminal_id: int) -> bool:
    """Kill a terminal process.
    
    Args:
        terminal_id: The terminal ID
        
    Returns:
        True if the terminal was killed, False otherwise
    """
    if terminal_id not in terminals:
        logger.warning(f"Terminal {terminal_id} not found")
        return False
    
    terminal = terminals[terminal_id]
    
    if not terminal["running"]:
        logger.warning(f"Terminal {terminal_id} is not running")
        return False
    
    try:
        # Kill the process
        terminal["process"].kill()
        terminal["running"] = False
        
        # Close the master end of the pty
        os.close(terminal["master"])
        
        logger.info(f"Killed terminal {terminal_id}")
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.error(f"Error killing terminal {terminal_id}: {e}")
        return False


def get_terminals() -> List[Dict[str, Any]]:
    """Get a list of all terminals.
    
    Returns:
        A list of terminal information dictionaries
    """
    return [
        {
            "id": terminal["id"],
            "command": terminal["command"],
            "cwd": terminal["cwd"],
            "running": terminal["running"]
        }
        for terminal in terminals.values()
    ]


def cleanup():
    """Clean up all terminals."""
    for terminal_id in list(terminals.keys()):
        kill_terminal(terminal_id)
    
    terminals.clear()
