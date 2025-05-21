"""
Terminal module for RA.Aid.

This module provides functionality for handling terminal input and output.
"""

from ra_aid.terminal.prompt_handler import start_prompt_handler
from ra_aid.terminal.handler import cleanup

__all__ = ["start_prompt_handler", "cleanup"]
