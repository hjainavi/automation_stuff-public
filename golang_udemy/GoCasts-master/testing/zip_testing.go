package main

import (
	"fmt"
	"os/exec"
)

func main() {
	/*

		abc := "before defer"
		defer func(abc string) {
			fmt.Println(abc)
		}(abc)
		files := []string{"/home/aviuser/testing/test1/debuglogs.20240712-094242_8c8ddc38/db/api_perf_stats_table_1day_19915.txt", "/home/aviuser/testing/test1/debuglogs.20240712-094242_8c8ddc38/db/se_stats_table_1day_19916.txt"}
		passphrase := "abcd"
		args := []string{"abc.zip"}
		args = append(args, files...)
		if passphrase != "" {
			args = append(args, []string{"-P", passphrase}...)
		}
		cmd := exec.Command("zip", args...)
		err := cmd.Run()
		if err != nil {
			fmt.Println(err)
		}
	*/
	cmd := exec.Command("python3", "/home/aviuser/testing/abc.py")
	//cmd = exec.Command("ls")
	//val, err := cmd.CombinedOutput()
	err := cmd.Run()
	if err != nil {
		fmt.Println(err.Error())
	}
	//_ = val
	//fmt.Printf("--- %s\n", val)

}
