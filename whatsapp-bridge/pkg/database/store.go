package database

import (
	"database/sql"
	"fmt"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

// Store handles database operations
type Store struct {
	db *sql.DB
}

// NewStore creates a new database store
func NewStore(dbPath, storeDir string) (*Store, error) {
	// Create directory if it doesn't exist
	if err := os.MkdirAll(storeDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create store directory: %w", err)
	}

	// Open database with proper configuration
	db, err := sql.Open("sqlite3", fmt.Sprintf("file:%s?_foreign_keys=on&_journal_mode=WAL", dbPath))
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// Set connection pool settings
	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(5)

	store := &Store{db: db}
	if err := store.initTables(); err != nil {
		db.Close()
		return nil, fmt.Errorf("failed to initialize tables: %w", err)
	}

	return store, nil
}

// Close closes the database connection
func (s *Store) Close() error {
	return s.db.Close()
}

// initTables creates the required database tables and indexes
func (s *Store) initTables() error {
	schema := `
		CREATE TABLE IF NOT EXISTS chats (
			jid TEXT PRIMARY KEY,
			name TEXT,
			last_message_time TIMESTAMP
		);
		
		CREATE TABLE IF NOT EXISTS messages (
			id TEXT,
			chat_jid TEXT,
			sender TEXT,
			content TEXT,
			timestamp TIMESTAMP,
			is_from_me BOOLEAN,
			media_type TEXT,
			filename TEXT,
			url TEXT,
			media_key BLOB,
			file_sha256 BLOB,
			file_enc_sha256 BLOB,
			file_length INTEGER,
			PRIMARY KEY (id, chat_jid),
			FOREIGN KEY (chat_jid) REFERENCES chats(jid)
		);

		-- Performance indexes
		CREATE INDEX IF NOT EXISTS idx_messages_chat_jid ON messages(chat_jid);
		CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
		CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender);
		CREATE INDEX IF NOT EXISTS idx_chats_last_message_time ON chats(last_message_time);
	`
	
	_, err := s.db.Exec(schema)
	return err
}

// StoreChat inserts or updates a chat record
func (s *Store) StoreChat(chat *Chat) error {
	_, err := s.db.Exec(
		"INSERT OR REPLACE INTO chats (jid, name, last_message_time) VALUES (?, ?, ?)",
		chat.JID, chat.Name, chat.LastMessageTime,
	)
	return err
}

// StoreMessage inserts or updates a message record
func (s *Store) StoreMessage(msg *Message) error {
	// Only store if there's actual content or media
	if msg.Content == "" && msg.MediaType == "" {
		return nil
	}

	_, err := s.db.Exec(`
		INSERT OR REPLACE INTO messages 
		(id, chat_jid, sender, content, timestamp, is_from_me, media_type, filename, url, media_key, file_sha256, file_enc_sha256, file_length) 
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		msg.ID, msg.ChatJID, msg.Sender, msg.Content, msg.Timestamp, msg.IsFromMe,
		msg.MediaType, msg.Filename, msg.URL, msg.MediaKey, msg.FileSHA256, msg.FileEncSHA256, msg.FileLength,
	)
	return err
}

// GetMessages retrieves messages for a chat with pagination
func (s *Store) GetMessages(chatJID string, limit, offset int) ([]*Message, error) {
	rows, err := s.db.Query(`
		SELECT id, chat_jid, sender, content, timestamp, is_from_me, media_type, filename, url, media_key, file_sha256, file_enc_sha256, file_length
		FROM messages 
		WHERE chat_jid = ? 
		ORDER BY timestamp DESC 
		LIMIT ? OFFSET ?`,
		chatJID, limit, offset,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []*Message
	for rows.Next() {
		msg := &Message{}
		err := rows.Scan(
			&msg.ID, &msg.ChatJID, &msg.Sender, &msg.Content, &msg.Timestamp,
			&msg.IsFromMe, &msg.MediaType, &msg.Filename, &msg.URL,
			&msg.MediaKey, &msg.FileSHA256, &msg.FileEncSHA256, &msg.FileLength,
		)
		if err != nil {
			return nil, err
		}
		messages = append(messages, msg)
	}

	return messages, rows.Err()
}

// GetChats retrieves all chats with pagination
func (s *Store) GetChats(limit, offset int) ([]*Chat, error) {
	rows, err := s.db.Query(`
		SELECT jid, name, last_message_time 
		FROM chats 
		ORDER BY last_message_time DESC 
		LIMIT ? OFFSET ?`,
		limit, offset,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var chats []*Chat
	for rows.Next() {
		chat := &Chat{}
		err := rows.Scan(&chat.JID, &chat.Name, &chat.LastMessageTime)
		if err != nil {
			return nil, err
		}
		chats = append(chats, chat)
	}

	return chats, rows.Err()
}