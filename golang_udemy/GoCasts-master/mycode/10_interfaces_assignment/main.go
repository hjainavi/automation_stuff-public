package main

import (
	"io"
	"log"
	"os"
)

func main() {
	args := os.Args
	file, err := os.Open(args[1]) // For read access.
	if err != nil {
		log.Fatal(err)
	}
	io.Copy(os.Stdout, file)
}
