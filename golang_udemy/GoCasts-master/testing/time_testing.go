package main

import (
	"fmt"
	"math"
)

var abc = 10

func test(depth float64) {
	fmt.Println("depth -- ", depth)
	fmt.Println("abc -- ", abc)
	abc -= 1
	if abc == 0 {
		return
	}
	if int(depth) == 0 {
		depth = math.Inf(1)
		fmt.Println("depth -- ", depth)

	}
	depth -= 1
	if depth > 0 {
		test(depth)
	}

}

func main() {
	fmt.Println("---")
	test(0)
}
