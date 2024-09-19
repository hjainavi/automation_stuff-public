package main

import (
	"fmt"
	"os"
	"path"
)

func main() {
	basePath := "/home/aviuser/a/"
	err := os.MkdirAll(basePath, os.ModePerm)
	if err != nil {
		fmt.Println(err)
		return
	}
	dname, err := os.MkdirTemp(basePath, "export_bundle")
	if err != nil {
		fmt.Println(err)
		return
	} else {
		fmt.Println(dname)
	}
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
}
