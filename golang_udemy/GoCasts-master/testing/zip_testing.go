package main

import (
	"exec"
	"fmt"
	"strings"
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
	/*
		cmd := exec.Command("python3", "/home/aviuser/testing/abc.py")
		//cmd = exec.Command("ls")
		//val, err := cmd.CombinedOutput()
		err := cmd.Run()
		if err != nil {
			fmt.Println(err.Error())
		}
	*/
	//
	checkConfigcmd := "/opt/avi/scripts/config_checker.py --config config.json --upgrade-log-taskjournal --clean-journal --taskjournal-file journal.json"
	cmdExec := exec.Command("python3", strings.Split(checkConfigcmd, " ")...)
	out, errF := cmdExec.CombinedOutput()
	fmt.Println(out)
	fmt.Println(errF)
	/*
		cmdExec := exec.Command("python3", strings.Split(checkConfigcmd, " ")...)
		out, errF := cmdExec.CombinedOutput()
		if errF != nil {
			avilog.Error(errF)
			avilog.Error(string(out))
			if exportCxt.RaiseErrorOnConfigExport() {
				return weberr.IntegrityError(string(out))
			}
		}
	*/
	//_ = val
	//fmt.Printf("--- %s\n", val)

}
