package main

import (
	"os"
	"testing"
)

func TestNewDeck(t *testing.T) {
	d := newDeck()
	if len(d) != 16 {
		t.Errorf("Expected deck length of 16 , but got %v", len(d))
	}
	if d[0] != "Ace of Spades" {
		t.Errorf("Expected first card as 'Ace of Spades' but got %v", d[0])
	}
	if d[len(d)-1] != "Four of Clubs" {
		t.Errorf("Expected last card as 'Four of Clubs' but got %v", d[len(d)-1])
	}
}

func TestSaveToFileandNewDeckFromFile(t *testing.T) {
	os.Remove("_decktesting.txt")

	d := newDeck()
	d.saveToFile("_decktesting.txt")
	loadedDeck := newDeckFromFile("_decktesting.txt")
	if len(loadedDeck) != 16 {
		t.Errorf("Expected deck from file to be of length of 16 , but got %v", len(d))
	}
	os.Remove("_decktesting.txt")

}
