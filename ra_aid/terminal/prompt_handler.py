"""
Terminal prompt handler for RA.Aid.

This module provides functionality to capture terminal prompts and send them to the frontend.
"""

import logging
import queue
import re
import threading
from typing import Dict, Any, Optional

from ra_aid.server.broadcast_sender import get_broadcast_queue

# Create logger
logger = logging.getLogger(__name__)

# Regular expression patterns for common terminal prompts
PROMPT_PATTERNS = [
    # Execute command prompt
    r"Execute this command\? \(y=yes, n=no, c=enable cowboy mode for session\)",
    # Other common prompts can be added here
]

# Global queue for terminal prompts
prompt_queue = queue.Queue()

# Flag to indicate if the prompt handler is running
is_running = False

# Current prompt being handled
current_prompt: Optional[Dict[str, Any]] = None


def start_prompt_handler():
    """Start the prompt handler thread."""
    global is_running
    
    if is_running:
        return
    
    is_running = True
    thread = threading.Thread(target=_prompt_handler_thread, daemon=True)
    thread.start()
    logger.info("Terminal prompt handler started")


def _prompt_handler_thread():
    """Thread function for handling terminal prompts."""
    global is_running, current_prompt
    
    while is_running:
        try:
            # Get the next prompt from the queue
            prompt = prompt_queue.get(timeout=1.0)
            
            # Set the current prompt
            current_prompt = prompt
            
            # Send the prompt to the frontend
            broadcast_queue = get_broadcast_queue()
            if broadcast_queue:
                broadcast_queue.put({
                    "type": "terminal_prompt",
                    "payload": prompt
                })
                logger.debug(f"Sent terminal prompt to frontend: {prompt}")
            
            # Wait for the response
            # The response will be handled by the handle_prompt_response function
            prompt_queue.task_done()
        except queue.Empty:
            # No prompt in the queue, continue
            pass
        except Exception as e:
            logger.error(f"Error in prompt handler thread: {e}")
            is_running = False


def detect_prompt(terminal_output: str) -> Optional[Dict[str, Any]]:
    """Detect if the terminal output contains a prompt.
    
    Args:
        terminal_output: The terminal output to check
        
    Returns:
        Dict with prompt information if a prompt is detected, None otherwise
    """
    for pattern in PROMPT_PATTERNS:
        match = re.search(pattern, terminal_output)
        if match:
            prompt_text = match.group(0)
            
            # Determine the prompt type
            prompt_type = "execute_command"
            
            # Determine the available options
            options = []
            if "y=yes" in prompt_text:
                options.append({"value": "y", "label": "Yes"})
            if "n=no" in prompt_text:
                options.append({"value": "n", "label": "No"})
            if "c=enable cowboy mode" in prompt_text:
                options.append({"value": "c", "label": "Cowboy Mode"})
            
            return {
                "type": prompt_type,
                "text": prompt_text,
                "options": options,
                "id": id(prompt_text)  # Use the id of the prompt text as a unique identifier
            }
    
    return None


def capture_terminal_output(terminal_output: str):
    """Capture terminal output and check for prompts.
    
    Args:
        terminal_output: The terminal output to check
    """
    prompt = detect_prompt(terminal_output)
    if prompt:
        prompt_queue.put(prompt)
        logger.debug(f"Captured terminal prompt: {prompt}")


def handle_prompt_response(response: str):
    """Handle a response to a terminal prompt.
    
    Args:
        response: The response to the prompt (e.g., "y", "n", "c")
    """
    global current_prompt
    
    if not current_prompt:
        logger.warning("No current prompt to handle response")
        return
    
    # Send the response to the terminal
    # This will be implemented in the terminal handler
    logger.debug(f"Handling prompt response: {response}")
    
    # Clear the current prompt
    current_prompt = None


def stop_prompt_handler():
    """Stop the prompt handler thread."""
    global is_running
    is_running = False
    logger.info("Terminal prompt handler stopped")
