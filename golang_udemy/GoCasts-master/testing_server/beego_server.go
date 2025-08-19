package main

import (
	"fmt"

	"github.com/beego/beego/v2/server/web"
)

// TestController handles requests to the /test endpoint
type TestController struct {
	web.Controller
}

// Get handles GET requests to /test
func (c *TestController) Get() {
	c.Ctx.Output.Header("Content-Type", "application/json")
	c.Data["json"] = map[string]interface{}{
		"message": "Hello from /test endpoint!",
		"method":  "GET",
		"status":  "success",
	}
	c.ServeJSON()
}

// Post handles POST requests to /test
func (c *TestController) Post() {
	c.Ctx.Output.Header("Content-Type", "application/json")
	c.Data["json"] = map[string]interface{}{
		"message": "POST request received at /test endpoint!",
		"method":  "POST",
		"status":  "success",
	}
	c.ServeJSON()
}

// HealthController handles the health check endpoint
type HealthController struct {
	web.Controller
}

// Get handles GET requests to /
func (c *HealthController) Get() {
	c.Ctx.Output.Header("Content-Type", "application/json")
	c.Data["json"] = map[string]interface{}{
		"message": "Server is running!",
		"status":  "success",
	}
	c.ServeJSON()
}

func main() {
	// Set the server port
	web.BConfig.Listen.HTTPPort = 9999

	// Disable Beego's default logging for cleaner output
	web.BConfig.Log.AccessLogs = false

	// Register routes
	web.Router("/test", &TestController{})
	web.Router("/", &HealthController{})

	fmt.Println("Starting Beego server on localhost:9999...\n")
	fmt.Println("Available endpoints:")
	fmt.Println("  - GET/POST /test - Test endpoint")
	fmt.Println("  - GET / - Health check\n")

	// Start the server
	web.Run()
}
