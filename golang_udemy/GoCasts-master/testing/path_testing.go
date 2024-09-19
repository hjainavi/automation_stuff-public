package main

import (
	"fmt"
	"os"
	"path"
	"time"
)

func main() {
	dname := "/home/aviuser/testing/tar_test2/abcdef11/avi_backup.tar.gz"
	fmt.Println(path.Base(path.Dir(dname)))
	tname, err := os.MkdirTemp("/home/aviuser/testing", "")
	if err != nil {
		fmt.Println(err)
	}
	err = os.Chmod(tname, 0755)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println(tname)
	fmt.Println(time.Now().Add(6 * time.Hour).UTC().Format(time.UnixDate))

}
