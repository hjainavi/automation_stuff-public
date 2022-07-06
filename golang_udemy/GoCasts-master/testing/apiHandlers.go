package main

import "fmt"

type CommonApiHandler struct{}

func (v *CommonApiHandler) Print() {
	fmt.Println("in common api handler print")
}

type BaseApiHandler struct {
	CommonApiHandler
}

type ListApiHandler struct {
	hdlr BaseApiHandler
}

func (v *ListApiHandler) Get() {
	v.hdlr.Print()
}

func main() {
	v := ListApiHandler{}
	v.hdlr = BaseApiHandler{}
	v.Get()
}
