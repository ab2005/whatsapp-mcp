package database

import (
	"time"
)

// Message represents a chat message
type Message struct {
	ID            string    `db:"id"`
	ChatJID       string    `db:"chat_jid"`
	Sender        string    `db:"sender"`
	Content       string    `db:"content"`
	Timestamp     time.Time `db:"timestamp"`
	IsFromMe      bool      `db:"is_from_me"`
	MediaType     string    `db:"media_type"`
	Filename      string    `db:"filename"`
	URL           string    `db:"url"`
	MediaKey      []byte    `db:"media_key"`
	FileSHA256    []byte    `db:"file_sha256"`
	FileEncSHA256 []byte    `db:"file_enc_sha256"`
	FileLength    uint64    `db:"file_length"`
}

// Chat represents a WhatsApp chat
type Chat struct {
	JID             string    `db:"jid"`
	Name            string    `db:"name"`
	LastMessageTime time.Time `db:"last_message_time"`
}

// IsGroup determines if a chat is a group based on JID pattern
func (c *Chat) IsGroup() bool {
	return len(c.JID) > 6 && c.JID[len(c.JID)-6:] == "@g.us"
}

// IsContact determines if a chat is a direct contact
func (c *Chat) IsContact() bool {
	return len(c.JID) > 13 && c.JID[len(c.JID)-13:] == "@s.whatsapp.net"
}