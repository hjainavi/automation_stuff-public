package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println(time.Now().UTC())

	fmt.Println(time.Now().Add(996 * time.Hour).UTC().Format(time.UnixDate))

}
