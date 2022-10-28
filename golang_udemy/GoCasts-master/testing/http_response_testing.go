package main

import (
	"crypto/tls"
	"fmt"

	"github.com/beego/beego/v2/client/httplib"
)

func main() {
	tlsConfig1 := tls.Config{}
	tlsConfig1.InsecureSkipVerify = true
	path := "https://100.65.9.177/api/pool"
	var req *httplib.BeegoHTTPRequest
	req = httplib.Get(path)
	req.SetTLSClientConfig(&tlsConfig1)
	req.SetBasicAuth("admin", "avi123")
	req.Header("HOST", "100.65.9.177")
	req.Header("X-AVI-VERSION", "22.1.3")
	req.Header("Content-Type", "application/json")
	req.Header("User-Agent", "Go-Apiserver-Internal/1.1")
	//req.JSONBody(requestData)
	resp, err := req.DoRequest()
	if err != nil {
		fmt.Println(err)
		return
	}
	/*
		var data interface{}
		err = json.NewDecoder(resp.Body).Decode(&data)
		if err != nil {
			fmt.Println(err)
		}
		defer resp.Body.Close()
	*/

	fmt.Println(resp.body)
	//dataf1 := data.(map[string]interface{})["results"].([]interface{})
	//dataf2 := dataf1[0].(map[string]interface{})
	//fmt.Println(dataf2["_last_modified"].(string))
	return

}
