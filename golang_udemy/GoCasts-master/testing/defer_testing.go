package main

import "fmt"

type RestartNginxReq struct {
	ForceNginxRestart *bool
}

func main() {
	abc := new(RestartNginxReq)
	fmt.Println(abc)

}
