package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	"whatsapp-client/pkg/validation"
)

// Response represents a standard API response
type Response struct {
	Success bool        `json:"success"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// SendMessageRequest represents the request body for sending messages
type SendMessageRequest struct {
	Recipient string `json:"recipient"`
	Message   string `json:"message"`
}

// SendFileRequest represents the request body for sending files
type SendFileRequest struct {
	Recipient string `json:"recipient"`
	FilePath  string `json:"file_path"`
}

// DownloadMediaRequest represents the request body for downloading media
type DownloadMediaRequest struct {
	MessageID string `json:"message_id"`
	ChatJID   string `json:"chat_jid"`
}

// writeJSONResponse writes a JSON response to the HTTP response writer
func writeJSONResponse(w http.ResponseWriter, statusCode int, response Response) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(response)
}

// writeErrorResponse writes an error response
func writeErrorResponse(w http.ResponseWriter, statusCode int, message string) {
	writeJSONResponse(w, statusCode, Response{
		Success: false,
		Error:   message,
	})
}

// writeSuccessResponse writes a success response
func writeSuccessResponse(w http.ResponseWriter, message string, data interface{}) {
	writeJSONResponse(w, http.StatusOK, Response{
		Success: true,
		Message: message,
		Data:    data,
	})
}

// parseJSONBody parses JSON request body into the provided struct
func parseJSONBody(r *http.Request, v interface{}) error {
	if r.Body == nil {
		return fmt.Errorf("request body is empty")
	}
	
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	
	if err := decoder.Decode(v); err != nil {
		return fmt.Errorf("invalid JSON: %w", err)
	}
	
	return nil
}

// validateSendMessageRequest validates a send message request
func validateSendMessageRequest(req SendMessageRequest) error {
	if err := validation.ValidateRecipient(req.Recipient); err != nil {
		return fmt.Errorf("invalid recipient: %w", err)
	}
	
	if err := validation.ValidateMessageContent(req.Message); err != nil {
		return fmt.Errorf("invalid message: %w", err)
	}
	
	return nil
}

// validateSendFileRequest validates a send file request
func validateSendFileRequest(req SendFileRequest) error {
	if err := validation.ValidateRecipient(req.Recipient); err != nil {
		return fmt.Errorf("invalid recipient: %w", err)
	}
	
	if err := validation.ValidateFilePath(req.FilePath); err != nil {
		return fmt.Errorf("invalid file path: %w", err)
	}
	
	return nil
}

// parseQueryParams parses common query parameters
func parseQueryParams(r *http.Request) (limit, offset int, err error) {
	limitStr := r.URL.Query().Get("limit")
	if limitStr == "" {
		limit = 20 // default
	} else {
		limit, err = strconv.Atoi(limitStr)
		if err != nil || limit < 1 || limit > 100 {
			return 0, 0, fmt.Errorf("invalid limit parameter")
		}
	}
	
	offsetStr := r.URL.Query().Get("offset")
	if offsetStr == "" {
		offset = 0 // default
	} else {
		offset, err = strconv.Atoi(offsetStr)
		if err != nil || offset < 0 {
			return 0, 0, fmt.Errorf("invalid offset parameter")
		}
	}
	
	return limit, offset, nil
}

// enableCORS sets CORS headers
func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
}