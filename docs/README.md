# WhatsApp MCP Documentation

Welcome to the WhatsApp MCP documentation. This directory contains comprehensive documentation for the WhatsApp Model Context Protocol (MCP) server.

## Documentation Overview

### 📋 [MCP Tools Reference](./mcp-tools.md)
Complete documentation of all 15 MCP tools available for WhatsApp integration:
- Contact and search operations
- Message operations with filtering and context
- Chat management tools
- Sending operations (text, files, voice messages)
- Media download capabilities

### 🔌 [API Reference](./api-reference.md)
Detailed REST API documentation for the Go WhatsApp Bridge:
- Endpoint specifications with examples
- Request/response formats
- Error handling and status codes
- Integration examples in multiple languages

### 🏗️ [Architecture Guide](./architecture.md)
In-depth system architecture documentation:
- Component design and interactions
- Data flow and storage architecture
- Security and performance considerations
- Scalability and future enhancements

## Quick Reference

### Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| **Contact** | `search_contacts` | Find contacts by name or phone |
| **Messages** | `list_messages`, `get_message_context` | Search and retrieve messages with context |
| **Chats** | `list_chats`, `get_chat`, `get_direct_chat_by_contact`, `get_contact_chats`, `get_last_interaction` | Chat management and discovery |
| **Sending** | `send_message`, `send_file`, `send_audio_message` | Send text, media, and voice messages |
| **Media** | `download_media` | Download and access media files |

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/send` | Send messages and files |
| `POST` | `/api/download` | Download media from messages |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/chats` | List chats (future) |
| `GET` | `/api/messages` | Get messages (future) |

### System Components

```
Claude Desktop ←→ Python MCP Server ←→ Go WhatsApp Bridge ←→ WhatsApp Web API
                        ↓                        ↓
                   SQLite Database        Local Media Storage
```

## Getting Started

1. **Setup:** Follow the installation guide in the main README
2. **Tools:** Review the [MCP Tools Reference](./mcp-tools.md) for available capabilities
3. **API:** Check the [API Reference](./api-reference.md) for direct integration
4. **Architecture:** Read the [Architecture Guide](./architecture.md) for system understanding

## Common Use Cases

### Basic Messaging
```python
# Search for a contact
contacts = search_contacts("John")

# Send a message
send_message("1234567890", "Hello!")

# Get recent messages
messages = list_messages(limit=10)
```

### Media Handling
```python
# Send a file
send_file("1234567890", "/path/to/document.pdf")

# Send voice message
send_audio_message("1234567890", "/path/to/audio.wav")

# Download media from message
result = download_media("msg123", "1234567890@s.whatsapp.net")
```

### Group Chats
```python
# Send to group (using JID)
send_message("123456789-123456789@g.us", "Group message")

# Find groups
groups = [chat for chat in list_chats() if chat["jid"].endswith("@g.us")]
```

### Conversation Context
```python
# Search messages with context
messages = list_messages(query="meeting", include_context=True)

# Get context around specific message
context = get_message_context("msg123", before=5, after=5)
```

## Security & Privacy

- **Local-First:** All data stored locally, no cloud dependencies
- **End-to-End Encryption:** WhatsApp's encryption is preserved
- **No Telemetry:** No data sent to external services
- **User Control:** Complete control over authentication and data

## Troubleshooting

### Common Issues

**Connection Problems:**
- Ensure Go bridge is running on port 8080
- Check WhatsApp session status (may need QR re-scan)
- Verify network connectivity

**Message Send Failures:**
- Confirm recipient format (phone number or JID)
- Check message length (<4096 characters)
- Verify WhatsApp session is active

**Media Issues:**
- Ensure file exists and is readable
- Check supported file types
- Verify sufficient storage space

### Getting Help

1. Check the specific documentation sections above
2. Review error messages for specific guidance
3. Verify system requirements and setup
4. Check GitHub issues for known problems

## Contributing

Documentation improvements are welcome! Please:

1. Follow the existing documentation structure
2. Include practical examples
3. Update all relevant sections for changes
4. Test examples before submitting

## Version Information

- **Current Version:** 1.0.0
- **Go Version:** 1.24.1
- **Python Version:** 3.11+
- **MCP Protocol:** 1.6.0+

For the latest updates and changes, see the main project README and GitHub releases.