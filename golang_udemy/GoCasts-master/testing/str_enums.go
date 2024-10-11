package main

import (
	"fmt"
	"strings"
)

type CallBackMethod string

const (
	CallbackPost   CallBackMethod = "post"
	CallbackPut    CallBackMethod = "put"
	CallbackDelete CallBackMethod = "delete"
)

type CallbackData struct {
	Pb     string
	Method CallBackMethod
}

func (c *CallbackData) GetMethod() CallBackMethod {
	return c.Method
}

func main() {
	//test := CallbackData{Pb: "abc"}
	test1 := CallbackData{Pb: "test1", Method: CallbackPost}
	fmt.Println(strings.ToLower(string(test1.GetMethod())))
	switch test1.GetMethod() {
	case "post":
		fmt.Println("case post")
	}
	/*
		fmt.Printf("%+v\n", test)
		fmt.Printf("%+v\n", test1)
		fmt.Println(test.Method == "")
		fmt.Println(test1.Method == CallbackDelete)
		fmt.Println(CallbackPut)
	*/
}
