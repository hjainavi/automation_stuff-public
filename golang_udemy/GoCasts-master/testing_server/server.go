package main

import (
	"fmt"
	"log"
	"net/http"
)

// testHandler handles requests to the /test endpoint
func testHandler(w http.ResponseWriter, r *http.Request) {
	// Set content type to JSON
	w.Header().Set("Content-Type", "application/json")

	// Check request method
	switch r.Method {
	case http.MethodGet:
		// Handle GET request
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"message": "Hello from /test endpoint!", "method": "GET", "status": "success"}`+"\n")
	case http.MethodPost:
		// Handle POST request
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"message": "POST request received at /test endpoint!", "method": "POST", "status": "success"}`+"\n")
	default:
		// Handle unsupported methods
		w.WriteHeader(http.StatusMethodNotAllowed)
		fmt.Fprintf(w, `{"error": "Method not allowed", "status": "error"}`+"\n")
	}
}

func main() {
	// Create a new HTTP server mux
	mux := http.NewServeMux()

	// Register the /test handler
	mux.HandleFunc("/test", testHandler)

	// Add a root handler for basic health check
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"message": "Server is running!", "status": "success"}`+"\n")
	})

	// Server configuration
	server := &http.Server{
		Addr:    ":8999",
		Handler: mux,
	}

	fmt.Println("Starting server on localhost:8999...\n")
	fmt.Println("Available endpoints:")
	fmt.Println("  - GET/POST /test - Test endpoint")
	fmt.Println("  - GET / - Health check\n")

	// Start the server
	log.Fatal(server.ListenAndServe())
}
