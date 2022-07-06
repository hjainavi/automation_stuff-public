package main

import (
	"fmt"
	"reflect"
)

type baseModel interface {
	printName()
	getNewModel()
}

type Pool struct {
	name string
	uuid string
}

func (p *Pool) printName() {
	fmt.Println(p.name)
}

func (p *Pool) getModelName() string {
	return "Pool"
}

func printModelName(b baseModel) {
	if b == nil {
		fmt.Println("Null")
	} else {
		abc := ""
		t := reflect.TypeOf(b)
		if t.Kind() == reflect.Ptr {
			abc = t.Elem().Name()
		} else {
			abc = t.Name()
		}
		fmt.Println(abc)
		fmt.Println(b.(t))
	}

}

func main() {
	p := &Pool{name: "test-pool", uuid: "uuid-pool"}
	printModelName(p)
}
