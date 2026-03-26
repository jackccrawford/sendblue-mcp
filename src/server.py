#!/usr/bin/env python3
"""
Sendblue MCP Server
Provides SMS/iMessage capabilities via Sendblue API
"""

import json
import os
from pathlib import Path
from typing import Optional

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize MCP server
mcp = FastMCP("sendblue")

# Load credentials
KEYS_FILE = Path.home() / ".keys" / "sendblue.json"

def load_credentials():
    """Load Sendblue API credentials from secure storage"""
    if not KEYS_FILE.exists():
        raise FileNotFoundError(f"Credentials file not found: {KEYS_FILE}")
    
    with open(KEYS_FILE) as f:
        return json.load(f)

CREDS = load_credentials()
API_KEY = CREDS["api_key"]
SECRET_KEY = CREDS["secret_key"]
CONTACTS = CREDS.get("contacts", {})

BASE_URL = "https://api.sendblue.co"


class SendMessageRequest(BaseModel):
    """Request model for sending SMS/iMessage"""
    number: str = Field(description="Phone number in E.164 format (e.g., +16029099450)")
    content: str = Field(description="Message content to send")
    send_style: Optional[str] = Field(
        default=None,
        description="Message style: 'invisible', 'gentle', 'loud', 'slam'. Default is standard."
    )


class ContactInfo(BaseModel):
    """Contact information"""
    name: str
    number: str


@mcp.tool()
async def send_sms(number: str, content: str, send_style: Optional[str] = None) -> dict:
    """
    Send an SMS or iMessage via Sendblue.
    
    Args:
        number: Phone number in E.164 format (e.g., +16029099450)
        content: Message text to send
        send_style: Optional message style ('invisible', 'gentle', 'loud', 'slam')
    
    Returns:
        dict: Response from Sendblue API including message status
    """
    headers = {
        "sb-api-key-id": API_KEY,
        "sb-api-secret-key": SECRET_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": number,
        "content": content
    }
    
    if send_style:
        payload["send_style"] = send_style
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/send-message",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_contacts() -> list[ContactInfo]:
    """
    Get list of saved contacts.
    
    Returns:
        list: Contact names and phone numbers
    """
    return [
        ContactInfo(name=name, number=number)
        for name, number in CONTACTS.items()
    ]


@mcp.tool()
async def check_message_status(account_email: str, number: str) -> dict:
    """
    Check delivery status of messages.
    
    Args:
        account_email: Your Sendblue account email
        number: Phone number to check status for
    
    Returns:
        dict: Message status information
    """
    headers = {
        "sb-api-key-id": API_KEY,
        "sb-api-secret-key": SECRET_KEY
    }
    
    params = {
        "accountEmail": account_email,
        "number": number
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/status",
            headers=headers,
            params=params,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def evaluate_service_type(number: str) -> dict:
    """
    Check if a number can receive iMessage or SMS.
    
    Args:
        number: Phone number in E.164 format
    
    Returns:
        dict: Service type information (iMessage or SMS)
    """
    headers = {
        "sb-api-key-id": API_KEY,
        "sb-api-secret-key": SECRET_KEY
    }
    
    params = {"number": number}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/evaluate-service",
            headers=headers,
            params=params,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    mcp.run()
