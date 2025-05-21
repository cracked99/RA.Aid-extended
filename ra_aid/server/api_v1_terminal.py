"""
API endpoints for terminal management.

This module provides API endpoints for managing terminals and handling terminal prompts.
"""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ra_aid.terminal.handler import (
    create_terminal,
    write_to_terminal,
    kill_terminal,
    get_terminals
)
from ra_aid.terminal.prompt_handler import handle_prompt_response

# Create logger
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/v1/terminal",
    tags=["terminal"],
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Server error"},
    },
)

class CreateTerminalRequest(BaseModel):
    """Request model for creating a terminal."""
    command: List[str] = Field(description="Command to run")
    cwd: Optional[str] = Field(None, description="Working directory")

class CreateTerminalResponse(BaseModel):
    """Response model for creating a terminal."""
    terminal_id: int = Field(description="Terminal ID")

class WriteTerminalRequest(BaseModel):
    """Request model for writing to a terminal."""
    data: str = Field(description="Data to write")

class TerminalPromptResponse(BaseModel):
    """Request model for responding to a terminal prompt."""
    response: str = Field(description="Response to the prompt")

class TerminalInfo(BaseModel):
    """Model for terminal information."""
    id: int = Field(description="Terminal ID")
    command: List[str] = Field(description="Command that was run")
    cwd: Optional[str] = Field(None, description="Working directory")
    running: bool = Field(description="Whether the terminal is running")

@router.post(
    "",
    response_model=CreateTerminalResponse,
    summary="Create a terminal",
    description="Create a new terminal process",
)
async def create_terminal_endpoint(request: CreateTerminalRequest) -> CreateTerminalResponse:
    """
    Create a new terminal process.
    
    Args:
        request: Request model with command and optional working directory
        
    Returns:
        Response model with terminal ID
        
    Raises:
        HTTPException: If there's an error creating the terminal
    """
    try:
        terminal_id = create_terminal(request.command, request.cwd)
        return CreateTerminalResponse(terminal_id=terminal_id)
    except Exception as e:
        logger.error(f"Error creating terminal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating terminal: {str(e)}",
        )

@router.post(
    "/{terminal_id}/write",
    summary="Write to a terminal",
    description="Write data to a terminal",
)
async def write_terminal_endpoint(terminal_id: int, request: WriteTerminalRequest) -> Dict[str, Any]:
    """
    Write data to a terminal.
    
    Args:
        terminal_id: Terminal ID
        request: Request model with data to write
        
    Returns:
        Dictionary with success status
        
    Raises:
        HTTPException: If the terminal is not found or there's an error writing to it
    """
    success = write_to_terminal(terminal_id, request.data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Terminal {terminal_id} not found or not running",
        )
    return {"success": True}

@router.post(
    "/prompt/response",
    summary="Respond to a terminal prompt",
    description="Send a response to a terminal prompt",
)
async def terminal_prompt_response_endpoint(request: TerminalPromptResponse) -> Dict[str, Any]:
    """
    Send a response to a terminal prompt.
    
    Args:
        request: Request model with response to the prompt
        
    Returns:
        Dictionary with success status
        
    Raises:
        HTTPException: If there's an error handling the prompt response
    """
    try:
        handle_prompt_response(request.response)
        return {"success": True}
    except Exception as e:
        logger.error(f"Error handling prompt response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error handling prompt response: {str(e)}",
        )

@router.delete(
    "/{terminal_id}",
    summary="Kill a terminal",
    description="Kill a terminal process",
)
async def kill_terminal_endpoint(terminal_id: int) -> Dict[str, Any]:
    """
    Kill a terminal process.
    
    Args:
        terminal_id: Terminal ID
        
    Returns:
        Dictionary with success status
        
    Raises:
        HTTPException: If the terminal is not found or there's an error killing it
    """
    success = kill_terminal(terminal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Terminal {terminal_id} not found or not running",
        )
    return {"success": True}

@router.get(
    "",
    response_model=List[TerminalInfo],
    summary="Get terminals",
    description="Get a list of all terminals",
)
async def get_terminals_endpoint() -> List[TerminalInfo]:
    """
    Get a list of all terminals.
    
    Returns:
        List of terminal information
    """
    return get_terminals()
