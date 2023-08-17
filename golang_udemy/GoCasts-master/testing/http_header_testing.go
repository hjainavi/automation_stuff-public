package main

import (
	"fmt"
	"net/http"
)

func main() {

	val := "x-AVI_VERSION"
	fmt.Println(http.CanonicalHeaderKey(val))
}
