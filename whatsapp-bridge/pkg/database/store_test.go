package database

import (
	"os"
	"testing"
	"time"
)

func TestNewStore(t *testing.T) {
	// Create temporary directory for test
	tempDir := t.TempDir()
	dbPath := tempDir + "/test.db"
	
	store, err := NewStore(dbPath, tempDir)
	if err != nil {
		t.Fatalf("Failed to create store: %v", err)
	}
	defer store.Close()
	
	// Verify database file was created
	if _, err := os.Stat(dbPath); os.IsNotExist(err) {
		t.Errorf("Database file was not created")
	}
}

func TestStoreChat(t *testing.T) {
	store, cleanup := setupTestStore(t)
	defer cleanup()
	
	chat := &Chat{
		JID:             "123456789@s.whatsapp.net",
		Name:            "Test Contact",
		LastMessageTime: time.Now(),
	}
	
	err := store.StoreChat(chat)
	if err != nil {
		t.Fatalf("Failed to store chat: %v", err)
	}
	
	// Verify chat was stored
	chats, err := store.GetChats(10, 0)
	if err != nil {
		t.Fatalf("Failed to get chats: %v", err)
	}
	
	if len(chats) != 1 {
		t.Errorf("Expected 1 chat, got %d", len(chats))
	}
	
	if chats[0].JID != chat.JID {
		t.Errorf("Expected JID %s, got %s", chat.JID, chats[0].JID)
	}
}

func TestStoreMessage(t *testing.T) {
	store, cleanup := setupTestStore(t)
	defer cleanup()
	
	// First store a chat
	chat := &Chat{
		JID:             "123456789@s.whatsapp.net",
		Name:            "Test Contact",
		LastMessageTime: time.Now(),
	}
	store.StoreChat(chat)
	
	message := &Message{
		ID:        "msg123",
		ChatJID:   chat.JID,
		Sender:    "123456789@s.whatsapp.net",
		Content:   "Test message",
		Timestamp: time.Now(),
		IsFromMe:  false,
	}
	
	err := store.StoreMessage(message)
	if err != nil {
		t.Fatalf("Failed to store message: %v", err)
	}
	
	// Verify message was stored
	messages, err := store.GetMessages(chat.JID, 10, 0)
	if err != nil {
		t.Fatalf("Failed to get messages: %v", err)
	}
	
	if len(messages) != 1 {
		t.Errorf("Expected 1 message, got %d", len(messages))
	}
	
	if messages[0].Content != message.Content {
		t.Errorf("Expected content %s, got %s", message.Content, messages[0].Content)
	}
}

func TestChatIsGroup(t *testing.T) {
	tests := []struct {
		jid      string
		expected bool
	}{
		{"123456789@s.whatsapp.net", false},
		{"123456789-123456789@g.us", true},
		{"invalid", false},
	}
	
	for _, test := range tests {
		chat := &Chat{JID: test.jid}
		result := chat.IsGroup()
		if result != test.expected {
			t.Errorf("For JID %s, expected IsGroup() = %v, got %v", test.jid, test.expected, result)
		}
	}
}

func TestChatIsContact(t *testing.T) {
	tests := []struct {
		jid      string
		expected bool
	}{
		{"123456789@s.whatsapp.net", true},
		{"123456789-123456789@g.us", false},
		{"invalid", false},
	}
	
	for _, test := range tests {
		chat := &Chat{JID: test.jid}
		result := chat.IsContact()
		if result != test.expected {
			t.Errorf("For JID %s, expected IsContact() = %v, got %v", test.jid, test.expected, result)
		}
	}
}

func setupTestStore(t *testing.T) (*Store, func()) {
	tempDir := t.TempDir()
	dbPath := tempDir + "/test.db"
	
	store, err := NewStore(dbPath, tempDir)
	if err != nil {
		t.Fatalf("Failed to create test store: %v", err)
	}
	
	cleanup := func() {
		store.Close()
	}
	
	return store, cleanup
}