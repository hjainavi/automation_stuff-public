package main

import (
	"fmt"
	"io"
	"os"
	"path"
)

func main() {
	/*
		_, err := copy("/tmp/abc/memprofile.out", "/tmp/memprofile1.out")
		if err != nil {
			fmt.Println(err)
		}
	*/
	fPath := "/tmp/abc/memprofile.out"
	fmt.Println(path.Base(fPath))
	cPath := "/tmp/tarfolder/"
	fmt.Println("creating ", path.Dir(path.Join(cPath, fPath)))
	err := os.MkdirAll(path.Dir(path.Join(cPath, fPath)), 0775)
	if err != nil {
		fmt.Println(err)
	}

}

func copy(src, dst string) (int64, error) {
	sourceFileStat, err := os.Stat(src)
	if err != nil {
		return 0, err
	}

	if !sourceFileStat.Mode().IsRegular() {
		return 0, fmt.Errorf("%s is not a regular file", src)
	}

	source, err := os.Open(src)
	if err != nil {
		return 0, err
	}
	defer source.Close()

	destination, err := os.Create(dst)
	if err != nil {
		return 0, err
	}
	defer destination.Close()
	nBytes, err := io.Copy(destination, source)
	return nBytes, err
}
