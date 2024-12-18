package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func main() {
	basePath := "/home/aviuser/a/"
	err := os.MkdirAll(basePath, os.ModePerm)
	if err != nil {
		fmt.Println(err)
		return
	}
	dname, err := os.MkdirTemp(basePath, "")
	if err != nil {
		fmt.Println(err)
		return
	} else {
		fmt.Println(dname)
	}
	/*
		finalPath1 := path.Join(dname, "avi_backup")
		err = os.Mkdir(finalPath1, 0750)
		if err != nil {
			fmt.Println(err)
			return
		}
		finalPath := path.Join(finalPath1, "avi.tar.gz")
		fmt.Println(finalPath)

		err = os.RemoveAll(path.Dir(finalPath))
		if err != nil {
			fmt.Println(err)
			return
		}
	*/
	files, err := os.ReadDir("/tmp/")
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("abc----", filepath.Dir("abc"))
	for _, file := range files {
		fileInfo, err := file.Info()
		if err != nil {
			fmt.Print(err)
			continue
		}
		if strings.Contains(fileInfo.Name(), "tmux") {
			fmt.Println(fileInfo.Name(), fileInfo.IsDir(), fileInfo.ModTime())
			fmt.Println(time.Now().Add(-3 * time.Hour))
			fmt.Println(fileInfo.ModTime().Compare(time.Now().Add(-3 * time.Hour)))
		}
	}

}
