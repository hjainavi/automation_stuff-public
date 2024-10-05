package main

import (
	"fmt"
)

func main() {
	abc := map[string]interface{}{"dbc": "111"}
	abc["aaa"] = 333
	fmt.Println(abc)
	//dataf1 := data.(map[string]interface{})["results"].([]interface{})
	//dataf2 := dataf1[0].(map[string]interface{})
	//fmt.Println(dataf2["_last_modified"].(string))

}
