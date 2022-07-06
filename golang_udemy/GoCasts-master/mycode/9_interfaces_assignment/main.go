package main

import "fmt"

type shape interface {
	getArea() float64
}

type triangle struct {
	base   float64
	height float64
}

func (t triangle) getArea() float64 {
	return 0.5 * t.base * t.height
}

type square struct {
	sideLength float64
}

func (s square) getArea() float64 {
	return s.sideLength * s.sideLength
}

func printArea(s shape) {
	fmt.Println(s.getArea())
}

func main() {
	sq := square{sideLength: 2.0}
	tr := triangle{base: 2.0, height: 2.0}

	printArea(sq)
	printArea(tr)
}
