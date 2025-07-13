package validation

import (
	"fmt"
	"path/filepath"
	"regexp"
	"strings"
)

var (
	// JID patterns for validation
	phoneJIDPattern = regexp.MustCompile(`^\d{10,15}@s\.whatsapp\.net$`)
	groupJIDPattern = regexp.MustCompile(`^\d+-\d+@g\.us$`)
	phonePattern    = regexp.MustCompile(`^\d{10,15}$`)
)

// ValidateJID validates WhatsApp JID format
func ValidateJID(jid string) error {
	if jid == "" {
		return fmt.Errorf("JID cannot be empty")
	}
	
	if phoneJIDPattern.MatchString(jid) || groupJIDPattern.MatchString(jid) {
		return nil
	}
	
	return fmt.Errorf("invalid JID format: %s", jid)
}

// ValidatePhoneNumber validates phone number format
func ValidatePhoneNumber(phone string) error {
	if phone == "" {
		return fmt.Errorf("phone number cannot be empty")
	}
	
	if !phonePattern.MatchString(phone) {
		return fmt.Errorf("invalid phone number format: %s (should be 10-15 digits)", phone)
	}
	
	return nil
}

// ValidateRecipient validates recipient (can be phone number or JID)
func ValidateRecipient(recipient string) error {
	if recipient == "" {
		return fmt.Errorf("recipient cannot be empty")
	}
	
	// Try phone number first
	if err := ValidatePhoneNumber(recipient); err == nil {
		return nil
	}
	
	// Try JID format
	if err := ValidateJID(recipient); err == nil {
		return nil
	}
	
	return fmt.Errorf("invalid recipient format: %s", recipient)
}

// ValidateFilePath validates and sanitizes file paths to prevent path traversal
func ValidateFilePath(path string) error {
	if path == "" {
		return fmt.Errorf("file path cannot be empty")
	}
	
	// Clean the path
	cleanPath := filepath.Clean(path)
	
	// Check for path traversal attempts
	if strings.Contains(cleanPath, "..") {
		return fmt.Errorf("path traversal detected in: %s", path)
	}
	
	// Convert to absolute path and check if it's within allowed directories
	absPath, err := filepath.Abs(cleanPath)
	if err != nil {
		return fmt.Errorf("invalid file path: %s", path)
	}
	
	// Additional security: ensure path doesn't contain null bytes
	if strings.Contains(absPath, "\x00") {
		return fmt.Errorf("invalid file path contains null byte: %s", path)
	}
	
	return nil
}

// ValidateMessageContent validates message content
func ValidateMessageContent(content string) error {
	if len(content) > 4096 { // WhatsApp message limit
		return fmt.Errorf("message content too long: %d characters (max 4096)", len(content))
	}
	
	return nil
}

// ValidateMediaType validates media file types
func ValidateMediaType(filename string) error {
	if filename == "" {
		return fmt.Errorf("filename cannot be empty")
	}
	
	ext := strings.ToLower(filepath.Ext(filename))
	allowedTypes := map[string]bool{
		".jpg":  true,
		".jpeg": true,
		".png":  true,
		".gif":  true,
		".webp": true,
		".mp4":  true,
		".mov":  true,
		".avi":  true,
		".mp3":  true,
		".wav":  true,
		".ogg":  true,
		".m4a":  true,
		".pdf":  true,
		".doc":  true,
		".docx": true,
		".txt":  true,
	}
	
	if !allowedTypes[ext] {
		return fmt.Errorf("unsupported media type: %s", ext)
	}
	
	return nil
}