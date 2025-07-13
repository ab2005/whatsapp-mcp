# WhatsApp MCP Architecture Documentation

This document provides a comprehensive overview of the WhatsApp MCP system architecture, component interactions, and design decisions.

## System Overview

The WhatsApp MCP is a two-component system that enables AI assistants to interact with WhatsApp through the Model Context Protocol (MCP). The system maintains a local-first approach with no cloud dependencies.

```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐    REST API    ┌─────────────────┐
│   Claude App    │◄──────────────────►│  Python MCP     │◄──────────────►│   Go WhatsApp   │
│   (AI Client)   │                    │    Server       │                │     Bridge      │
└─────────────────┘                    └─────────────────┘                └─────────────────┘
                                                │                                   │
                                                ▼                                   ▼
                                       ┌─────────────────┐                ┌─────────────────┐
                                       │   SQLite DB     │                │  WhatsApp Web   │
                                       │   (Messages)    │                │      API        │
                                       └─────────────────┘                └─────────────────┘
```

## Component Architecture

### 1. Go WhatsApp Bridge

**Purpose:** Handle WhatsApp Web API communication and local message storage.

**Key Responsibilities:**
- Maintain persistent WhatsApp Web connection using `whatsmeow` library
- Handle QR code authentication and session management
- Store messages and chat metadata in SQLite database
- Provide REST API for message sending and media download
- Manage media file caching and storage

**Technology Stack:**
- **Language:** Go 1.24.1
- **WhatsApp Library:** whatsmeow (WhatsApp Web multidevice API)
- **Database:** SQLite3 with WAL mode for concurrent access
- **HTTP Server:** Standard Go net/http
- **Authentication:** QR code scanning for WhatsApp Web

**Directory Structure:**
```
whatsapp-bridge/
├── main.go                 # Main application entry point
├── pkg/
│   ├── config/            # Configuration management
│   ├── database/          # Database models and operations
│   ├── validation/        # Input validation utilities
│   └── api/              # HTTP API handlers
├── store/                 # Local data storage
│   ├── messages.db       # SQLite message database
│   ├── whatsapp.db      # WhatsApp session storage
│   └── media/           # Downloaded media files
└── go.mod                # Go module dependencies
```

### 2. Python MCP Server

**Purpose:** Implement MCP protocol and provide structured tools for AI interaction.

**Key Responsibilities:**
- Implement Model Context Protocol using FastMCP framework
- Provide 15 structured tools for WhatsApp operations
- Handle data validation and sanitization
- Communicate with Go bridge via HTTP API
- Audio format conversion using FFmpeg

**Technology Stack:**
- **Language:** Python 3.11+
- **MCP Framework:** FastMCP for protocol implementation
- **HTTP Client:** requests for API communication
- **Audio Processing:** FFmpeg for voice message conversion
- **Package Manager:** UV for modern Python dependency management

**Directory Structure:**
```
whatsapp-mcp-server/
├── src/
│   ├── config.py         # Configuration management
│   ├── models.py         # Data models and schemas
│   ├── database.py       # Database operations
│   ├── validation.py     # Input validation
│   ├── api_client.py     # HTTP API client
│   └── __init__.py
├── tests/                # Comprehensive test suite
├── main.py              # MCP server entry point
├── whatsapp.py          # Legacy implementation (to be refactored)
├── audio.py             # Audio processing utilities
└── pyproject.toml       # Python project configuration
```

## Data Flow Architecture

### Message Sending Flow

```
1. Claude ──MCP──► Python Server ──validation──► HTTP API ──► Go Bridge ──► WhatsApp API
                                                                    │
2. WhatsApp API ──response──► Go Bridge ──JSON──► Python Server ──MCP──► Claude
```

### Message Receiving Flow

```
1. WhatsApp API ──webhook──► Go Bridge ──store──► SQLite Database
                                 │
2. Python Server ──query──► SQLite Database ──results──► MCP Tools ──► Claude
```

### Media Handling Flow

```
1. Media Upload: Client ──► Python Server ──► Go Bridge ──► WhatsApp Servers
2. Media Download: WhatsApp Servers ──► Go Bridge ──cache──► Local Storage
3. Media Access: Python Server ──► Local Storage ──► MCP Tools ──► Claude
```

## Database Schema

### Messages Database (SQLite)

**Chats Table:**
```sql
CREATE TABLE chats (
    jid TEXT PRIMARY KEY,           -- WhatsApp JID
    name TEXT,                      -- Display name
    last_message_time TIMESTAMP     -- Last activity
);

-- Performance indexes
CREATE INDEX idx_chats_last_message_time ON chats(last_message_time);
```

**Messages Table:**
```sql
CREATE TABLE messages (
    id TEXT,                        -- Message ID
    chat_jid TEXT,                  -- Reference to chats.jid
    sender TEXT,                    -- Sender JID
    content TEXT,                   -- Message content
    timestamp TIMESTAMP,            -- Message timestamp
    is_from_me BOOLEAN,            -- Sent by current user
    media_type TEXT,               -- Media type (image/video/audio/document)
    filename TEXT,                 -- Original filename
    url TEXT,                      -- WhatsApp media URL
    media_key BLOB,                -- Encryption key
    file_sha256 BLOB,              -- File hash
    file_enc_sha256 BLOB,          -- Encrypted file hash
    file_length INTEGER,           -- File size
    PRIMARY KEY (id, chat_jid),
    FOREIGN KEY (chat_jid) REFERENCES chats(jid)
);

-- Performance indexes
CREATE INDEX idx_messages_chat_jid ON messages(chat_jid);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_sender ON messages(sender);
```

### WhatsApp Session Database

Managed by whatsmeow library for session persistence and device information.

## API Design

### REST API (Go Bridge)

**Base URL:** `http://localhost:8080/api`

**Endpoints:**
- `POST /send` - Send messages and files
- `POST /download` - Download media
- `GET /health` - Health check
- `GET /chats` - List chats (future)
- `GET /messages` - Get messages (future)

**Design Principles:**
- RESTful URL structure
- Consistent JSON response format
- Proper HTTP status codes
- Input validation and sanitization
- Error handling with descriptive messages

### MCP Tools (Python Server)

**Tool Categories:**
- **Contact Operations:** search_contacts
- **Message Operations:** list_messages, get_message_context
- **Chat Operations:** list_chats, get_chat, get_direct_chat_by_contact, get_contact_chats, get_last_interaction
- **Sending Operations:** send_message, send_file, send_audio_message
- **Media Operations:** download_media

**Design Principles:**
- Declarative tool definitions with clear parameters
- Consistent return value structures
- Comprehensive input validation
- Rich error messages and status information
- Pagination support for large datasets

## Security Architecture

### Authentication & Authorization

**WhatsApp Authentication:**
- QR code scanning for initial setup
- Session persistence (~20 days)
- Automatic session renewal
- Device management through WhatsApp app

**API Security:**
- Local-only access (localhost binding)
- Input validation and sanitization
- Path traversal prevention
- File type validation
- No external authentication (future consideration)

### Data Security

**Local Storage:**
- All data stored locally in SQLite
- No cloud storage or external APIs
- Media files cached locally
- Database encryption possible (future)

**Input Validation:**
- Recipient format validation (phone/JID)
- File path sanitization
- Content length limits
- Media type restrictions
- SQL injection prevention

### Privacy Considerations

- **No Telemetry:** No data sent to external services
- **Local Processing:** All operations performed locally
- **User Control:** Complete control over data and access
- **Encryption:** WhatsApp end-to-end encryption preserved
- **Session Management:** User controls authentication lifecycle

## Performance Architecture

### Database Optimization

**Indexing Strategy:**
```sql
-- Core indexes for common queries
CREATE INDEX idx_messages_chat_timestamp ON messages(chat_jid, timestamp);
CREATE INDEX idx_messages_sender_timestamp ON messages(sender, timestamp);
CREATE INDEX idx_chats_last_active ON chats(last_message_time DESC);
```

**Connection Management:**
- Connection pooling (max 10 connections)
- WAL mode for concurrent reads
- Prepared statements for common queries
- Transaction boundaries for related operations

### Caching Strategy

**Media Caching:**
- On-demand media download
- Local file system cache
- LRU eviction policy (future)
- Configurable cache size limits

**Query Caching:**
- In-memory caching for frequently accessed data
- Chat list caching
- Contact information caching

### Concurrency Model

**Go Bridge:**
- Goroutine-based concurrency
- Channel communication for event handling
- Mutex protection for shared state
- Connection pooling for database access

**Python Server:**
- Synchronous request handling (current)
- Async/await support (future enhancement)
- Thread-safe database operations

## Scalability Considerations

### Current Limitations

- Single WhatsApp account per instance
- Local SQLite database (no clustering)
- Synchronous Python processing
- Local file storage only

### Future Scalability Enhancements

**Database:**
- PostgreSQL support for larger datasets
- Read replicas for improved query performance
- Database sharding for multi-account support

**Storage:**
- Distributed media storage
- CDN integration for media delivery
- Automatic media cleanup policies

**Processing:**
- Async Python implementation
- Message queue for background processing
- Horizontal scaling support

## Deployment Architecture

### Development Setup

```
Developer Machine:
├── Go Bridge (Port 8080)
├── Python MCP Server (stdio)
├── SQLite Database (local)
├── Media Storage (local)
└── Claude Desktop (MCP client)
```

### Production Considerations

**Containerization:**
```dockerfile
# Multi-stage Docker build
FROM golang:1.24.1-alpine AS go-builder
FROM python:3.11-slim AS final
# Combined runtime with both components
```

**Process Management:**
- Systemd services for Linux
- Process monitoring and restart
- Log aggregation and rotation
- Health check endpoints

**Network Security:**
- Firewall rules (localhost only)
- TLS/SSL for API (future)
- VPN access for remote use
- Network isolation

## Error Handling & Reliability

### Error Categories

**WhatsApp Connectivity:**
- Session expiration
- Network connectivity issues
- Rate limiting from WhatsApp
- Device deauthorization

**Database Errors:**
- Connection failures
- Lock timeouts
- Disk space issues
- Schema migrations

**Media Handling:**
- File not found
- Unsupported formats
- Download failures
- Storage quota exceeded

### Reliability Measures

**Retry Logic:**
- Exponential backoff for API calls
- Circuit breaker pattern
- Dead letter queues for failed operations

**Data Integrity:**
- Database transactions
- Backup and recovery procedures
- Consistency checks
- Migration validation

**Monitoring:**
- Health check endpoints
- Metrics collection
- Error tracking and alerting
- Performance monitoring

## Future Architecture Evolution

### Planned Enhancements

**Multi-Account Support:**
- Account isolation and management
- Separate database per account
- Load balancing across accounts

**Real-time Features:**
- WebSocket support for live updates
- Event streaming to clients
- Push notifications

**Advanced Search:**
- Full-text search with indexing
- Vector embeddings for semantic search
- Advanced query capabilities

**Integration Features:**
- Webhook support for external systems
- Plugin architecture for extensions
- Third-party service integrations

### Migration Strategy

**Component Isolation:**
- Clear interface boundaries
- Backward compatibility maintenance
- Phased rollout of new features
- A/B testing capabilities

**Data Migration:**
- Schema versioning and migration tools
- Backward compatibility for data formats
- Export/import capabilities
- Data validation and cleanup tools