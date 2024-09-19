package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	ch := make(chan *int, 4)
	array := []int{1, 2, 3, 4}
	wg := sync.WaitGroup{}
	wg.Add(1)
	go func() {
		for _, value := range array {
			fmt.Println(&value)
			ch <- &value
		}
		// Close channel to reach wg.Done() line.
		close(ch)
	}()
	time.Sleep(2 * time.Second)
	go func() {
		for value := range ch {
			fmt.Println(*value)
		}
		wg.Done()
	}()
	wg.Wait()
}
