package main

import "fmt"

type user struct{}

type exampleInterface interface {
	getGreeting(string, int) (string, error)
	getBotVersion() int
	respondToUser(user) string
}

type bot interface {
	getGreeting() string
}

/*
	The above declaration states
	to whom it may concern:
		"type bot interface"
	our program has a new type called "bot"
		"getGreeting() string"
	If there is a type in this program with a function called 'getGreeting'
	and you return a string then you are a honorary member of type 'bot'
	Now that you are a member of type 'bot'
	you can call the function called 'printGreeting' since it accepts type bot:
		func printGreeting(b bot)

*/

type englishBot struct{}
type spanishBot struct{}

func (englishBot) getGreeting() string {
	// assume custom logic for getting the greeting for each bot
	// removed receiver variable since we are not using it
	return "Hello there!"
}

func (spanishBot) getGreeting() string {
	// assume custom logic for getting the greeting for each bot
	return "Hola!"
}

/*
printGreeting cannot be defined twice with different arguments in go
printgreeting has same logic for both englishBot and spanishBot
func printGreeting(eb englishBot) {
	fmt.Println(eb.getGreeting)
}
func printGreeting(sb spanishBot) {
	fmt.Println(sb.getGreeting)
}
*/

func printGreeting(b bot) {
	fmt.Println(b.getGreeting())
}

func main() {
	eb := englishBot{}
	sb := spanishBot{}
	printGreeting(eb)
	printGreeting(sb)
}
