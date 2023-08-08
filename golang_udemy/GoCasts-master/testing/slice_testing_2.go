package main

import "fmt"

func main() {
	abc := []float64{1, 2, 3, 4, 5, 6, 7, 8, 9}
	newAbc := []float64{}
	item := 5.5
	index := 9
	newAbc = append(newAbc, abc[:index]...)
	newAbc = append(newAbc, item)
	newAbc = append(newAbc, abc[index:]...)
	//newAbc = append(newAbc, abc[index:]...)
	//fmt.Println(abc[:index])
	//fmt.Println(abc[index:])
	fmt.Println("abc == ", abc)
	fmt.Println("newAbc == ", newAbc)
}
