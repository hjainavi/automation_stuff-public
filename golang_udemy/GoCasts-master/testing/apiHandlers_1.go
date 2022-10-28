package main

import "fmt"

// Here we are defining the global variable and assigning value to it
type abc struct {
	sss string
}

func (val *abc) Print() {
	fmt.Println(val.sss)
}

type abcI interface {
	Print()
}

func main() {
	val1 := abc{sss: "val1"}
	val2 := abc{sss: "val2"}
	list := []abcI{&val1, &val2}
	fmt.Println("1")
	display(list)
	fmt.Println("2")
	display(nil)
	fmt.Println("3")
	display([]abcI{})
}
func display(val []abcI) {
	if len(val) != 0 {
		fmt.Println(val)
	}
}
