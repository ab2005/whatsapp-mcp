# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Go WhatsApp Bridge (in whatsapp-bridge/)
- **Run bridge**: `go run main.go`
- **Windows setup**: Enable CGO first with `go env -w CGO_ENABLED=1`, then run

### Python MCP Server (in whatsapp-mcp-server/)
- **Run server**: `uv run main.py`
- **Install dependencies**: `uv sync`

## Architecture

This is a two-component system enabling WhatsApp integration via MCP:

```
Claude Desktop <--MCP--> Python Server <--REST API--> Go Bridge <--WhatsApp Web API--> WhatsApp
                                |                          |
                                v                          v
                         SQLite DB (messages)      WhatsApp session DB
```

### Key Components

**Go Bridge (whatsapp-bridge/)**
- Maintains WhatsApp Web connection using whatsmeow library
- Exposes REST API on port 8080 with endpoints:
  - `/api/send` - Send messages/media
  - `/api/download` - Download media files
- Stores messages in SQLite database at `store/messages.db`
- QR code authentication on first run

**Python MCP Server (whatsapp-mcp-server/)**
- Implements MCP tools for WhatsApp operations
- Communicates with Go bridge via HTTP
- Handles media conversion (audio to Opus format via FFmpeg)
- Main entry point: `main.py`

### Database Schema

**messages.db**
- `chats` table: jid (PK), name, last_message_time
- `messages` table: id, chat_jid (composite PK), sender, content, timestamp, is_from_me, media metadata

### MCP Tools

All WhatsApp operations are exposed as MCP tools:
- Message operations: search_messages, list_messages, get_message_context
- Chat operations: list_chats, get_chat, search_contacts
- Send operations: send_message, send_file, send_audio_message
- Media operations: download_media

### Media Handling

- **Sending**: Files uploaded through Go bridge to WhatsApp servers
- **Voice messages**: Must be .ogg Opus format (auto-converted with FFmpeg)
- **Downloading**: Media metadata stored in DB, actual files downloaded on demand
- **Storage**: Media cached in `store/` directory structure

### Important Notes

- WhatsApp session persists for ~20 days before re-authentication needed
- All data stored locally - no cloud storage
- Group messages require JID format (e.g., "groupid@g.us")
- Media files are not automatically downloaded - use download_media tool when needed