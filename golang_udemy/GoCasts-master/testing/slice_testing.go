package main

import "fmt"

func main() {
	var abc []int
	abc = make([]int, 2)
	test(abc)
	fmt.Println("in main Value", abc)
}

func test(abc []int) {
	abc[0] = 10
	fmt.Println("in test value", abc)
}
