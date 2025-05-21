"""
Workspace utilities for managing the RA.Aid workspace directory.

This module provides functions for managing the workspace directory,
including resetting it to a clean state.
"""

import logging
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple, List

from ra_aid.logging_config import get_logger

logger = get_logger(__name__)

def reset_workspace(workspace_dir: Optional[str] = None) -> Tuple[bool, str]:
    """
    Reset the workspace directory to a clean state.

    This function removes all files and directories in the workspace directory,
    effectively creating a fresh environment for new projects.

    Args:
        workspace_dir: Optional path to the workspace directory.
                      If not provided, uses the PROJECT_STATE_DIR environment variable.

    Returns:
        Tuple[bool, str]: (success, message) where success is True if the operation
                         was successful, and message contains details about the operation.
    """
    # Get workspace directory from environment variable if not provided
    if not workspace_dir:
        workspace_dir = os.environ.get("PROJECT_STATE_DIR")

    if not workspace_dir:
        return False, "Workspace directory not specified and PROJECT_STATE_DIR environment variable not set."

    workspace_path = Path(workspace_dir)

    if not workspace_path.exists():
        return False, f"Workspace directory does not exist: {workspace_dir}"

    if not workspace_path.is_dir():
        return False, f"Workspace path is not a directory: {workspace_dir}"

    try:
        logger.info(f"Starting workspace reset for directory: {workspace_path}")

        # Get list of all items in the directory
        items = list(workspace_path.iterdir())

        if not items:
            logger.info(f"Workspace is already empty: {workspace_path}")
            return True, "Workspace is already empty."

        # Track what was removed for logging
        removed_dirs: List[str] = []
        removed_files: List[str] = []

        # Remove all files and directories in the workspace
        for item in items:
            # Skip .ra-aid directory if it exists (to preserve configuration)
            if item.name == ".ra-aid":
                logger.info(f"Skipping .ra-aid directory to preserve configuration: {item}")
                continue

            if item.is_dir():
                logger.info(f"Removing directory: {item}")
                shutil.rmtree(item)
                removed_dirs.append(item.name)
            else:
                logger.info(f"Removing file: {item}")
                item.unlink()
                removed_files.append(item.name)

        # Create a detailed message about what was removed
        message_parts = []
        if removed_dirs:
            dirs_msg = f"Removed {len(removed_dirs)} directories: {', '.join(removed_dirs)}"
            message_parts.append(dirs_msg)
            logger.info(dirs_msg)

        if removed_files:
            files_msg = f"Removed {len(removed_files)} files: {', '.join(removed_files)}"
            message_parts.append(files_msg)
            logger.info(files_msg)

        if message_parts:
            message = "Workspace reset successfully. " + ", ".join(message_parts) + "."
        else:
            message = "Workspace reset successfully, but no files or directories were removed."

        logger.info(f"Workspace reset complete: {message}")
        return True, message

    except Exception as e:
        error_message = f"Error resetting workspace: {str(e)}"
        logger.error(error_message)
        return False, error_message
