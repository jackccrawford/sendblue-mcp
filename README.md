# Sendblue MCP

SMS/iMessage for AI agents — secure, polling-based, no webhooks required.

Your agent needs to send campaign messages and check for replies. Traditional webhook approaches expose your local machine to the internet. Sendblue MCP uses API polling instead — zero attack surface, zero infrastructure, zero security risk.

```python
# Send a message
send_sms(number="+15551234567", content="Campaign message here")

# Check for replies (no webhooks needed)
list_messages(is_outbound=False, limit=10)
```

47 messages later, across sessions, your agent remembers the conversation context.

## About Sendblue

[Sendblue](https://sendblue.co) is the SMS/iMessage API that powers this server. They handle message delivery, phone number management, iMessage detection, and delivery status tracking. This MCP server is a wrapper — it connects your AI agent to Sendblue's REST API using polling instead of webhooks.

You'll need a Sendblue account and API credentials to use this tool. Sign up at [sendblue.co](https://sendblue.co) and get your keys from the [dashboard](https://app.sendblue.co).

**This project is not affiliated with Sendblue.** It's an independent open-source MCP server built on their public API.

## End-to-end: what this actually looks like

**Monday — Campaign launch.** Your agent sends 50 outreach messages:

```python
for contact in campaign_list:
    send_sms(number=contact.phone, content=personalized_message)
```

**Tuesday — Check responses.** Different session, different agent:

```python
replies = list_messages(is_outbound=False, limit=50)
# Agent sees: 12 replies, 3 interested, 9 opt-outs
```

No webhook setup. No public endpoints. No ngrok. Just secure API polling.

**Why polling beats webhooks for campaigns:**
- ✅ No exposed services on your machine
- ✅ No infrastructure to maintain
- ✅ Campaign responses aren't real-time anyway
- ✅ Zero security risk to genesis station
- ✅ Works from anywhere (no static IP needed)

## Works with everything

Windsurf, Claude Desktop, any MCP-compatible client. One Poetry environment. No runtime dependencies beyond Python 3.11+.

## Install

**1. Clone and install:**

```bash
git clone https://github.com/jackccrawford/sendblue-mcp.git
cd sendblue-mcp
poetry install --no-root
```

**2. Configure credentials:**

Create `~/.keys/sendblue.json`:

```json
{
  "api_key": "your_sendblue_api_key",
  "secret_key": "your_sendblue_secret_key",
  "from_number": "+15559876543",
  "contacts": {
    "alice": "+15551234567",
    "bob": "+15559998888"
  }
}
```

Get your credentials from [Sendblue Dashboard](https://app.sendblue.co).

**3. Add to MCP config:**

Windsurf (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "sendblue": {
      "command": "/Users/YOUR_USERNAME/.local/bin/poetry",
      "args": [
        "-C",
        "/Users/YOUR_USERNAME/Dev/sendblue-mcp",
        "run",
        "python",
        "src/server.py"
      ],
      "env": {
        "FASTMCP_BANNER": "0",
        "PYTHONWARNINGS": "ignore"
      }
    }
  }
}
```

Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sendblue": {
      "command": "poetry",
      "args": ["-C", "/path/to/sendblue-mcp", "run", "python", "src/server.py"]
    }
  }
}
```

**4. Restart your MCP client** (Windsurf, Claude Desktop, etc.)

## What it looks like

**Send a message:**

```python
send_sms(
    number="+15551234567",
    content="Test from Sendblue MCP! 🚀"
)
# Returns: {"status": "QUEUED", "message_handle": "...", "from_number": "+15559876543"}
```

**Check for replies:**

```python
list_messages(is_outbound=False, limit=10)
# Returns: [{"content": "Interested!", "from_number": "+15551234567", ...}, ...]
```

**Get your contacts:**

```python
get_contacts()
# Returns: [{"name": "alice", "number": "+15551234567"}, {"name": "bob", "number": "+15559998888"}]
```

**Check if a number supports iMessage:**

```python
evaluate_service_type(number="+15551234567")
# Returns: {"number": "+15551234567", "service": "iMessage"}
```

## How it works

Sendblue MCP is a FastMCP server backed by httpx for async API calls. No webhooks. No background services. No public endpoints.

```
Agent → MCP Server (FastMCP) → Sendblue API (HTTPS)
```

Messages are sent via Sendblue's REST API. Replies are retrieved by polling `/api/v2/messages` when you ask. Content stays in Sendblue's cloud until you fetch it.

**Security model:**
- Credentials stored locally in `~/.keys/sendblue.json` (mode 0600)
- No public endpoints exposed
- No webhook receivers
- No attack surface on your machine
- API calls are outbound-only (HTTPS to Sendblue)

## Tools

### `send_sms(number, content, send_style=None)`

Send an SMS or iMessage via Sendblue.

**Args:**
- `number` (str): Phone number in E.164 format (e.g., `+15551234567`)
- `content` (str): Message text to send
- `send_style` (str, optional): Message style - `'invisible'`, `'gentle'`, `'loud'`, `'slam'`

**Returns:**
```json
{
  "status": "QUEUED",
  "message_handle": "35d2bd01-5fe0-4ee3-a9fd-a61231e0ddd4",
  "from_number": "+15559876543",
  "to_number": "+15551234567",
  "date_sent": "2026-03-26T22:14:40.696Z"
}
```

### `list_messages(limit=10, is_outbound=False, offset=0)`

List recent messages (inbound or outbound). Polls Sendblue API without requiring webhooks.

**Args:**
- `limit` (int): Number of messages to retrieve (default: 10, max: 100)
- `is_outbound` (bool): `False` for received messages, `True` for sent messages
- `offset` (int): Pagination offset (default: 0)

**Returns:**
```json
{
  "messages": [
    {
      "content": "Interested in learning more!",
      "from_number": "+15551234567",
      "to_number": "+15559876543",
      "is_outbound": false,
      "status": "RECEIVED",
      "date_sent": "2026-03-26T22:30:15.123Z"
    }
  ]
}
```

### `get_contacts()`

Get list of saved contacts from credentials file.

**Returns:**
```json
[
  {"name": "alice", "number": "+15551234567"},
  {"name": "bob", "number": "+15559998888"}
]
```

### `check_message_status(account_email, number)`

Check delivery status of messages.

**Args:**
- `account_email` (str): Your Sendblue account email
- `number` (str): Phone number to check status for

**Returns:**
```json
{
  "status": "DELIVERED",
  "last_message": "2026-03-26T22:14:40.696Z"
}
```

### `evaluate_service_type(number)`

Check if a number can receive iMessage or SMS.

**Args:**
- `number` (str): Phone number in E.164 format

**Returns:**
```json
{
  "number": "+15551234567",
  "service": "iMessage"
}
```

## Security considerations

**Why no webhooks?**

Traditional webhook approaches require exposing your local machine to the internet (via ngrok, Tailscale Funnel, etc.). This creates an attack surface on your development machine where sensitive assets live (genesis station, credentials, code).

**Polling is safer:**
- No public endpoints
- No inbound connections
- No webhook receiver code to exploit
- API calls are outbound-only
- You control when messages are fetched

**For sales campaigns, polling is sufficient:**
- Responses aren't real-time (people take hours/days to reply)
- Checking every few minutes is fast enough
- Zero infrastructure complexity
- Zero security risk

**If you need real-time webhooks:**
- Deploy webhook receiver on isolated server (not your Mac)
- Use dedicated droplet with no privileged access
- Forward messages to queue/database
- MCP polls the queue (still no webhooks on your machine)

## Dependencies

- Python 3.11+
- FastMCP 2.0+
- httpx 0.28+
- pydantic 2.10+

All managed via Poetry. No system dependencies.

## License

MIT

## About

Built for mVara's sales campaign automation. Designed for security-conscious teams who eliminated ngrok and need safe two-way messaging.

**Repository:** https://github.com/jackccrawford/sendblue-mcp  
**Issues:** https://github.com/jackccrawford/sendblue-mcp/issues  
**Sendblue API:** https://docs.sendblue.com
