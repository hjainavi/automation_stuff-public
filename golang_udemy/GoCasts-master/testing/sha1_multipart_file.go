package main

import (
	"crypto/sha1"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
)

func main() {

	filepath := "/home/aviuser/AviGeoDb.txt.gz"
	fmt.Println(SHA256Checksum(filepath))
	fmt.Println(HashFileSha1(filepath))

}

func SHA256Checksum(path string) (string, error) {
	return SHA256ChecksumTillSize(path, -1)
}

func SHA256ChecksumTillSize(path string, size int64) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}

	defer func() {
		_ = f.Close()
	}()
	if size == -1 {
		stat, err := f.Stat()
		if err != nil {
			return "", err
		}
		size = stat.Size()
	}

	buf := make([]byte, 1024*1024)
	h := sha256.New()

	var totalRead int64 = 0
	for {
		bytesRead, err := f.Read(buf)
		if err != nil {
			if err != io.EOF {
				fmt.Println("Error while getting file checksum, err:", err)
				return "", err
			}
			break
		}
		// read only till size
		if totalRead+int64(bytesRead) >= size {
			bytesRead = int(size - totalRead)
		}
		h.Write(buf[:bytesRead])
		totalRead += int64(bytesRead)
		// break when done
		if totalRead == size {
			break
		}
	}

	return hex.EncodeToString(h.Sum(nil)), nil
}

func HashFileSha1(filePath string) (string, error) {
	var returnSHA1String string
	file, err := os.Open(filePath)
	if err != nil {
		return returnSHA1String, err
	}
	defer file.Close()
	hash := sha1.New()
	if _, err := io.Copy(hash, file); err != nil {
		return returnSHA1String, err
	}
	hashInBytes := hash.Sum(nil)
	returnSHA1String = hex.EncodeToString(hashInBytes)
	return returnSHA1String, nil
}
