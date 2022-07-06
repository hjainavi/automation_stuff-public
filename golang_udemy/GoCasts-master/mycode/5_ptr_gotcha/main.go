package main

import "fmt"

func main() {
	mySlice := []string{"1", "2", "3", "4", "5"}
	// whenever we create a slice data structure , it is basically a ptr to an underlying array
	// slice is a type containing three elemnts ptrToHeadofArray,length,capacity
	// slice in Golang is a reference type data structure
	updateSlice(mySlice)
	fmt.Println(mySlice)
}

func updateSlice(s []string) {
	s[0] = "1111"
}
