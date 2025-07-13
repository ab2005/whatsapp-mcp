# WhatsApp Bridge API Reference

This document provides detailed API documentation for the WhatsApp Bridge REST API component.

## Base URL

```
http://localhost:8080/api
```

## Authentication

Currently, no authentication is required. Future versions may implement API key authentication.

## Content Types

- `application/json` for JSON requests/responses
- `multipart/form-data` for file uploads

## Common Response Format

All API responses follow a consistent structure:

```json
{
  "success": boolean,
  "message": "Status message",
  "data": {},  // Optional response data
  "error": "Error description"  // Only present on errors
}
```

---

## Endpoints

### POST /send

Send a text message or file to a WhatsApp recipient.

#### Request Types

**Text Message:**
```json
{
  "recipient": "1234567890",
  "message": "Hello, world!"
}
```

**File Path:**
```json
{
  "recipient": "1234567890", 
  "file_path": "/absolute/path/to/file.jpg"
}
```

**File Upload (multipart/form-data):**
```
recipient: 1234567890
file: [binary file data]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| recipient | string | Yes | Phone number (10-15 digits) or JID |
| message | string | Yes* | Text message content (max 4096 chars) |
| file_path | string | Yes* | Absolute path to file to send |
| file | binary | Yes* | File upload for multipart requests |

*One of `message`, `file_path`, or `file` is required.

#### Recipient Formats

- **Phone Number:** `"1234567890"` (10-15 digits, no symbols)
- **Contact JID:** `"1234567890@s.whatsapp.net"`  
- **Group JID:** `"123456789-123456789@g.us"`

#### Supported File Types

| Category | Extensions |
|----------|------------|
| Images | .jpg, .jpeg, .png, .gif, .webp |
| Videos | .mp4, .mov, .avi |
| Audio | .mp3, .wav, .ogg, .m4a |
| Documents | .pdf, .doc, .docx, .txt |

#### Response

**Success (200):**
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "message_id": "3EB0C767D26A1D8D6E73"
  }
}
```

**Error (400):**
```json
{
  "success": false,
  "error": "Invalid recipient format"
}
```

#### Example Requests

**Text Message:**
```bash
curl -X POST http://localhost:8080/api/send \
  -H "Content-Type: application/json" \
  -d '{"recipient": "1234567890", "message": "Hello!"}'
```

**File Upload:**
```bash
curl -X POST http://localhost:8080/api/send \
  -F "recipient=1234567890" \
  -F "file=@/path/to/image.jpg"
```

**Group Message:**
```bash
curl -X POST http://localhost:8080/api/send \
  -H "Content-Type: application/json" \
  -d '{"recipient": "123456789-123456789@g.us", "message": "Group message"}'
```

---

### POST /download

Download media from a WhatsApp message.

#### Request

```json
{
  "message_id": "3EB0C767D26A1D8D6E73",
  "chat_jid": "1234567890@s.whatsapp.net"
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| message_id | string | Yes | ID of the message containing media |
| chat_jid | string | Yes | JID of the chat containing the message |

#### Response

**Success (200):**
```json
{
  "success": true,
  "message": "Media downloaded successfully", 
  "file_path": "/app/store/media/image_123.jpg"
}
```

**Error (404):**
```json
{
  "success": false,
  "error": "Media not found or already deleted"
}
```

#### Example Request

```bash
curl -X POST http://localhost:8080/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "3EB0C767D26A1D8D6E73",
    "chat_jid": "1234567890@s.whatsapp.net"
  }'
```

---

### GET /health

Health check endpoint to verify API availability.

#### Response

**Success (200):**
```json
{
  "status": "healthy",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

#### Example Request

```bash
curl http://localhost:8080/api/health
```

---

### GET /chats

List WhatsApp chats with pagination.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 20 | Maximum number of chats (1-100) |
| offset | integer | 0 | Number of chats to skip |

#### Response

**Success (200):**
```json
{
  "success": true,
  "data": {
    "chats": [
      {
        "jid": "1234567890@s.whatsapp.net",
        "name": "John Doe", 
        "last_message_time": "2023-01-01T12:00:00Z",
        "is_group": false,
        "is_contact": true
      }
    ],
    "total": 150,
    "limit": 20,
    "offset": 0
  }
}
```

#### Example Request

```bash
curl "http://localhost:8080/api/chats?limit=50&offset=20"
```

---

### GET /messages

Get messages from a specific chat.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_jid | string | Yes | JID of the chat |
| limit | integer | No | Maximum messages (1-100, default: 20) |
| offset | integer | No | Messages to skip (default: 0) |

#### Response

**Success (200):**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "3EB0C767D26A1D8D6E73",
        "chat_jid": "1234567890@s.whatsapp.net",
        "sender": "1234567890@s.whatsapp.net", 
        "content": "Hello!",
        "timestamp": "2023-01-01T12:00:00Z",
        "is_from_me": false,
        "media_type": null,
        "filename": null
      }
    ],
    "total": 500,
    "limit": 20,
    "offset": 0
  }
}
```

#### Example Request

```bash
curl "http://localhost:8080/api/messages?chat_jid=1234567890@s.whatsapp.net&limit=10"
```

---

## Error Codes

| HTTP Code | Description | Common Causes |
|-----------|-------------|---------------|
| 400 | Bad Request | Invalid input, malformed JSON, missing required fields |
| 404 | Not Found | Message/media not found, invalid chat JID |
| 500 | Internal Server Error | Database errors, WhatsApp connection issues |

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting for production use.

## Data Models

### Chat Object

```json
{
  "jid": "string",           // WhatsApp JID
  "name": "string",          // Display name
  "last_message_time": "datetime", // ISO-8601 timestamp
  "is_group": boolean,       // True for group chats
  "is_contact": boolean      // True for direct contacts
}
```

### Message Object

```json
{
  "id": "string",            // Unique message ID
  "chat_jid": "string",      // Chat containing this message
  "sender": "string",        // Message sender JID
  "content": "string",       // Text content
  "timestamp": "datetime",   // ISO-8601 timestamp
  "is_from_me": boolean,     // True if sent by current user
  "media_type": "string",    // "image", "video", "audio", "document", null
  "filename": "string"       // Original filename (for media)
}
```

## Integration Examples

### Python

```python
import requests

# Send a message
response = requests.post(
    "http://localhost:8080/api/send",
    json={"recipient": "1234567890", "message": "Hello!"}
)
result = response.json()

# Download media  
response = requests.post(
    "http://localhost:8080/api/download",
    json={
        "message_id": "msg123",
        "chat_jid": "1234567890@s.whatsapp.net"
    }
)
download_result = response.json()
```

### JavaScript

```javascript
// Send a message
const response = await fetch('http://localhost:8080/api/send', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    recipient: '1234567890',
    message: 'Hello!'
  })
});
const result = await response.json();

// Upload a file
const formData = new FormData();
formData.append('recipient', '1234567890');
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8080/api/send', {
  method: 'POST',
  body: formData
});
```

### Go

```go
import (
    "bytes"
    "encoding/json"
    "net/http"
)

type SendRequest struct {
    Recipient string `json:"recipient"`
    Message   string `json:"message"`
}

// Send a message
req := SendRequest{
    Recipient: "1234567890", 
    Message:   "Hello!",
}
jsonData, _ := json.Marshal(req)

resp, err := http.Post(
    "http://localhost:8080/api/send",
    "application/json",
    bytes.NewBuffer(jsonData),
)
```

## WebSocket Support (Future)

Future versions may include WebSocket support for real-time message notifications:

```
ws://localhost:8080/ws/messages
```

## Security Considerations

- **Local Network Only:** API should only be accessible on localhost/private network
- **Input Validation:** All inputs are validated to prevent injection attacks  
- **File Validation:** Uploaded files are validated for type and size
- **Path Safety:** File paths are sanitized to prevent directory traversal
- **No Authentication:** Consider adding API key authentication for production

## Troubleshooting

### Common Issues

**Connection Refused:**
- Ensure WhatsApp bridge is running on port 8080
- Check firewall settings

**Message Send Failures:**
- Verify WhatsApp session is active (check QR code authentication)
- Confirm recipient format is correct
- Check internet connectivity

**File Upload Issues:**
- Verify file exists and is readable
- Check file type is supported
- Ensure file size is reasonable (<100MB recommended)

**Media Download Failures:**
- Message may not contain media
- Media may have been deleted from WhatsApp servers
- Check storage space availability