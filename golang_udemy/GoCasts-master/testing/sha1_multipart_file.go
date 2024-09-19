package main

import (
	"crypto/sha1"
	"fmt"
	"io"
	"os"
)

func main() {

	filePath := "/var/www/html/home.tar.gz"
	wholeChecksum(filePath)

}

func wholeChecksum(filePath string) {

	file, err := os.Open(filePath)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	hash := sha1.New()
	if _, err := io.Copy(hash, file); err != nil {
		fmt.Println("Error calculating checksum:", err)
		return
	}

	checksum := fmt.Sprintf("%x", hash.Sum(nil))
	fmt.Println("whole SHA1 checksum:", checksum)

}
