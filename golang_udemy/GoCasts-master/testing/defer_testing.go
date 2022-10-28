package main

import "fmt"

var i int

func main() {
	test()
}

// Now, count is evaluated inside `printCount`, so it will
// only be called when the deferred function executes
func test() {
	var abc []string
	fmt.Println("defer count:", count)
}
