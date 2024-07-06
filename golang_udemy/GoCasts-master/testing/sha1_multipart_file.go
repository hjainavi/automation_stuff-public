package main

import (
	"bufio"
	"crypto/sha1"
	"fmt"
	"io"
	"os"
)

func main() {
	filePath := "path/to/your/file"
	partChecksum(filePath)
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

func partChecksum(filePath string) {

	file, err := os.Open(filePath)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	hash := sha1.New()
	const chunkSize = 64 * 1024 // 64 KB chunks
	reader := bufio.NewReader(file)
	buf := make([]byte, chunkSize)

	for {
		n, err := reader.Read(buf)
		if err != nil && err != io.EOF {
			fmt.Println("1111    ", err)
			return
		}
		if n == 0 {
			break
		}
		n, err = hash.Write(buf)
		if err != nil {
			fmt.Println("2222    ", err)
			return
		}
	}

	checksum := fmt.Sprintf("%x", hash.Sum(nil))
	fmt.Println("part SHA1 checksum:", checksum)
}
