package main

import (
	"fmt"
)

func main() {
	var abc []int
	abc = make([]int, 2)
	test(abc)
	fmt.Println("in main Value", abc)
	abc1()
	/*
		for i := 0; i < 10; i++ {
			if testFunc(1) && testFunc(2) {
				// do nothing
			}
		}
	*/
}

func testFunc(i int) bool {
	fmt.Printf("function %d called\n", i)
	return false
}

func test(abc []int) {
	abc[0] = 10
	fmt.Println("in test value", abc)
}

func abc1() {
	//var err error
	/*
		var1 := make(map[string][]string, 0)
		var1["abc"] = append(var1["abc"], "2")
		var1["abc"] = append(var1["abc"], "2")

		fmt.Println(slices.Contains(var1["abc"], "2"))
		fmt.Println(var1["def22"] == nil)
		fmt.Println(var1)
	var2 := make(map[string]bool, 0)
	fmt.Println(var2["def"] == true)
	fmt.Println(var2["deff"])
	var3 := make(map[string]string, 0)
	fmt.Println(var3["abc"] == "")

	fmt.Println(var3["abc1"])
	fmt.Println(err == nil)
	*/

	var1 := make(map[string][]string, 0)
	var1["abc"] = []string{"a1","a2"}
	val, ok := var1.(interface{})
	if ok {
		fmt.Printf("%+v", val)
	}



}
