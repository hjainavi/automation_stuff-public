package main

import (
	"fmt"
)

func main() {
	abc := map[string]interface{}{"abc": "def", "123": 123}
	fmt.Println("abc %+v", abc)

	var a interface{}
	a = abc
	def := a.(map[string]interface{})
	fmt.Println("def %+v", def)
}
