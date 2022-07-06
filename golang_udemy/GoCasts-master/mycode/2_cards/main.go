package main

// card1 := "abc" // shot type decl cannot be used outside function body

func main() {
	// var card string = "Ace of Spades"
	//cards := deck{"Ace of Diamonds", newCard()} // slice of type string
	//cards = append(cards, "Six of Spades")
	cards := newDeck()
	cards.saveToFile("cards.txt")

	newCard := newDeckFromFile("cards.txt")
	newCard.print()
	newCard.shuffle()
	newCard.print()

}

/*
func newCard() string {
	return "Five of Diamonds"
}
*/
