# Sendblue MCP Server

MCP server for Sendblue SMS/iMessage API integration.

## Features

- Send SMS/iMessage via Sendblue API
- Check message delivery status
- Evaluate service type (iMessage vs SMS)
- Manage contacts

## Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Configure credentials in `~/.keys/sendblue.json`:
   ```json
   {
     "api_key": "your_api_key",
     "secret_key": "your_secret_key",
     "contacts": {
       "name": "+1234567890"
     }
   }
   ```

3. Add to Windsurf MCP config (`~/.codeium/windsurf/mcp_config.json`):
   ```json
   {
     "sendblue": {
       "command": "poetry",
       "args": ["-C", "/Users/mars/Dev/sendblue-mcp", "run", "python", "src/server.py"]
     }
   }
   ```

## Usage

The MCP server provides these tools:
- `send_sms` - Send SMS/iMessage
- `get_contacts` - List saved contacts
- `check_message_status` - Check delivery status
- `evaluate_service_type` - Check if number supports iMessage
