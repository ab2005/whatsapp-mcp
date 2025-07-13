package config

import (
	"os"
	"strconv"
)

// Config holds application configuration
type Config struct {
	DatabasePath string
	APIPort      int
	StoreDir     string
	LogLevel     string
}

// LoadConfig loads configuration from environment variables with defaults
func LoadConfig() *Config {
	config := &Config{
		DatabasePath: getEnv("WHATSAPP_DB_PATH", "store/messages.db"),
		APIPort:      getEnvAsInt("WHATSAPP_API_PORT", 8080),
		StoreDir:     getEnv("WHATSAPP_STORE_DIR", "store"),
		LogLevel:     getEnv("WHATSAPP_LOG_LEVEL", "info"),
	}
	return config
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}