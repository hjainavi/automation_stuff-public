package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
)

/*
	program to do a http request to google.com and print it out
*/
type logWriter struct{}

func (l logWriter) Write(bs []byte) (int, error) {
	fmt.Println(string(bs))
	fmt.Println("we just wrote", len(bs), "bytes")
	return len(bs), nil
}

func main() {
	resp, err := http.Get("http://www.google.com")

	if err != nil {
		fmt.Println("Error:", err)
		os.Exit(1)
	}
	/*
		responseBody := make([]byte, 99999)
		// initilizing empty byte slice with space 99999
		// assuming that total data is not more than 9999
		resp.Body.Read(responseBody)
		fmt.Println(string(responseBody))
	*/
	//io.Copy(os.Stdout, resp.Body)
	lw := logWriter{}
	io.Copy(lw, resp.Body)

}
