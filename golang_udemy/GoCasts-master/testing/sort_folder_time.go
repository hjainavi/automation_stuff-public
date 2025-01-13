package main

import (
	"fmt"
	"sort"
	"time"
)

func main() {
	// Sample map with string keys and time.Time values
	m := map[string]time.Time{
		"event1":  time.Date(2022, 12, 10, 9, 0, 0, 0, time.UTC),
		"event2":  time.Date(2023, 5, 20, 10, 0, 0, 0, time.UTC),
		"event3":  time.Date(2021, 7, 5, 12, 0, 0, 0, time.UTC),
		"event4":  time.Date(2023, 1, 1, 8, 0, 0, 0, time.UTC),
		"event5":  time.Date(2020, 3, 15, 7, 0, 0, 0, time.UTC),
		"event6":  time.Date(2024, 11, 30, 14, 0, 0, 0, time.UTC),
		"event7":  time.Date(2019, 6, 18, 16, 0, 0, 0, time.UTC),
		"event8":  time.Date(2025, 2, 25, 17, 0, 0, 0, time.UTC),
		"event9":  time.Date(2022, 10, 12, 18, 0, 0, 0, time.UTC),
		"event10": time.Date(2021, 8, 13, 20, 0, 0, 0, time.UTC),
		"event11": time.Date(2023, 12, 5, 10, 0, 0, 0, time.UTC),
		"event12": time.Date(2024, 5, 25, 11, 0, 0, 0, time.UTC),
		"event13": time.Date(2020, 7, 21, 13, 0, 0, 0, time.UTC),
		"event14": time.Date(2018, 9, 15, 15, 0, 0, 0, time.UTC),
		"event15": time.Date(2025, 4, 10, 19, 0, 0, 0, time.UTC),
		"event16": time.Date(2023, 3, 8, 21, 0, 0, 0, time.UTC),
	}

	// Create a slice of keys
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}

	// Sort the slice of keys based on the values in the map in descending order
	sort.Slice(keys, func(i, j int) bool {
		return m[keys[i]].After(m[keys[j]])
	})

	// Iterate over the sorted slice of keys, but only print up to index 9
	for i, k := range keys {
		if i < 10 {
			continue
		}
		fmt.Printf("%s: %v\n", k, m[k])
	}
}
