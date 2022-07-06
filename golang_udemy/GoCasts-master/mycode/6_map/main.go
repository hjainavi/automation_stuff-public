package main

import "fmt"

func main() {
	/*
		// map with keys as strings and values as string
		colors := map[string]string{
			"red":   "#ff0000",
			"green": "$4b8768",
		}
		fmt.Println(colors)
	*/

	// var colors map[string]string

	colors := make(map[string]string)

	colors["red"] = "#ff0000"
	colors["white"] = "#000000"
	colors["green"] = "#bf0098"
	// delete(colors, "white")
	// fmt.Println(colors)
	printMap(colors)

}

func printMap(c map[string]string) {
	for key, val := range c {
		fmt.Println(key, val)
	}
}
