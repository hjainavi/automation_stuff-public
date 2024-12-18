package main

import (
	"fmt"
)

func main() {
	a := 2
	defer func(a int) {
		fmt.Println(a)
	}(a)
	a = 3
	fmt.Println("after ", a)

}
