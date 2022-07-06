package main

import (
	"fmt"
	"net/http"
)

func main() {
	links := []string{
		"http://www.google.com",
		"http://www.facebook.com",
		"http://www.golang.org",
		"http://www.amazon.com",
	}
	c := make(chan string)

	for _, link := range links {
		go checkLink(c, link) // go keyword launches new go routines
	}
	for range links {
		<-c // channel receving a value is a blocking call
	}

}

func checkLink(c chan string, link string) {
	_, err := http.Get(link)
	if err != nil {
		fmt.Println(link, "might be down")
		c <- ""
		return
	}
	fmt.Println(link, "is up!")
	c <- ""

}
