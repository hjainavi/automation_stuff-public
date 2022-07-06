package main

import (
	"fmt"
	"io/ioutil"
	"math/rand"
	"os"
	"strings"
	"time"
)

// Create a new type of deck
// which is a slice of strings

type deck []string

func newDeck() deck {
	// create a new deck of cards
	cards := deck{}

	cardSuits := []string{"Spades", "Diamonds", "Hearts", "Clubs"}
	cardValues := []string{"Ace", "Two", "Three", "Four"}
	for _, suit := range cardSuits {
		for _, value := range cardValues {
			cards = append(cards, value+" of "+suit)
		}
	}
	return cards
}

func (d deck) print() {
	// receiver function
	// print all the cards in the deck
	for i, card := range d {
		fmt.Println(i, card)
	}
}

func deal(d deck, handSize int) (deck, deck) {
	// using deck as an argument ( no receiver )
	// deal the cards to the player acc. to the handsize
	// and remove those cards from the deck
	return d[:handSize], d[handSize:]
}

func (d deck) toString() string {
	// type conversion from type deck to type slice of strings
	return strings.Join([]string(d), "\n")
}

func (d deck) saveToFile(filename string) error {
	return ioutil.WriteFile(filename, []byte(d.toString()), 0666)
}

func newDeckFromFile(filename string) deck {
	bs, err := ioutil.ReadFile(filename)
	if err != nil {
		// option #1 - log the error and retrn a call to newDeck()
		// option #2 - log the error and entirely quit the program
		fmt.Println("Error:", err)
		os.Exit(1)
	}
	s := strings.Split(string(bs), "\n")
	return deck(s)
}

func (d deck) shuffle() {
	rand.Seed(time.Now().UnixNano())
	for i := 0; i < len(d); i++ {
		randomPos := rand.Intn(len(d))
		d[i], d[randomPos] = d[randomPos], d[i]
	}
}

//func saveToFile()
/*
func (d deck) print() {} == receiver on a function
Any variable of type "deck" now gets access to the print "method"
*/
