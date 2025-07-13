package validation

import (
	"os"
	"path/filepath"
	"testing"
)

func TestValidateJID(t *testing.T) {
	tests := []struct {
		jid     string
		wantErr bool
	}{
		{"123456789@s.whatsapp.net", false},
		{"123456789-123456789@g.us", false},
		{"", true},
		{"invalid", true},
		{"123@invalid.domain", true},
	}
	
	for _, test := range tests {
		err := ValidateJID(test.jid)
		if (err != nil) != test.wantErr {
			t.Errorf("ValidateJID(%s) error = %v, wantErr %v", test.jid, err, test.wantErr)
		}
	}
}

func TestValidatePhoneNumber(t *testing.T) {
	tests := []struct {
		phone   string
		wantErr bool
	}{
		{"1234567890", false},
		{"123456789012345", false},
		{"", true},
		{"123", true},
		{"12345678901234567890", true},
		{"abc1234567890", true},
	}
	
	for _, test := range tests {
		err := ValidatePhoneNumber(test.phone)
		if (err != nil) != test.wantErr {
			t.Errorf("ValidatePhoneNumber(%s) error = %v, wantErr %v", test.phone, err, test.wantErr)
		}
	}
}

func TestValidateRecipient(t *testing.T) {
	tests := []struct {
		recipient string
		wantErr   bool
	}{
		{"1234567890", false},
		{"123456789@s.whatsapp.net", false},
		{"123456789-123456789@g.us", false},
		{"", true},
		{"invalid", true},
	}
	
	for _, test := range tests {
		err := ValidateRecipient(test.recipient)
		if (err != nil) != test.wantErr {
			t.Errorf("ValidateRecipient(%s) error = %v, wantErr %v", test.recipient, err, test.wantErr)
		}
	}
}

func TestValidateFilePath(t *testing.T) {
	// Create temporary test file
	tempDir := t.TempDir()
	testFile := filepath.Join(tempDir, "test.txt")
	err := os.WriteFile(testFile, []byte("test"), 0644)
	if err != nil {
		t.Fatalf("Failed to create test file: %v", err)
	}
	
	tests := []struct {
		path    string
		wantErr bool
	}{
		{testFile, false},
		{"", true},
		{"/nonexistent/file.txt", true},
		{"../../../etc/passwd", true},
		{"/dev/null\x00", true},
	}
	
	for _, test := range tests {
		err := ValidateFilePath(test.path)
		if (err != nil) != test.wantErr {
			t.Errorf("ValidateFilePath(%s) error = %v, wantErr %v", test.path, err, test.wantErr)
		}
	}
}

func TestValidateMessageContent(t *testing.T) {
	tests := []struct {
		content string
		wantErr bool
	}{
		{"Hello", false},
		{"", true},
		{string(make([]byte, 5000)), true}, // Too long
	}
	
	for _, test := range tests {
		err := ValidateMessageContent(test.content)
		if (err != nil) != test.wantErr {
			t.Errorf("ValidateMessageContent() error = %v, wantErr %v", err, test.wantErr)
		}
	}
}

func TestValidateMediaType(t *testing.T) {
	tests := []struct {
		filename string
		wantErr  bool
	}{
		{"image.jpg", false},
		{"video.mp4", false},
		{"document.pdf", false},
		{"", true},
		{"malicious.exe", true},
		{"script.js", true},
	}
	
	for _, test := range tests {
		err := ValidateMediaType(test.filename)
		if (err != nil) != test.wantErr {
			t.Errorf("ValidateMediaType(%s) error = %v, wantErr %v", test.filename, err, test.wantErr)
		}
	}
}