package main

import "fmt"

// Here we are defining the global variable and assigning value to it

func main() {
	abc := 10
	display(&abc)
	display(nil)
}
func display(abc *int) {
	if abc == nil {
		s := 10
		abc = &s
	}
	fmt.Printf("The Global variable glvariable's inside function value is : %v\n",
		abc)
}
