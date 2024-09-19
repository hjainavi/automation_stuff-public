package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strings"
)

func main() {
	plan, _ := ioutil.ReadFile("/tmp/avi_config_customer.json")
	var config map[string]interface{}
	err := json.Unmarshal(plan, &config)
	if err != nil {
		fmt.Println(err.Error())
		return
	}
	for key, value := range config {
		vals, ok := value.([]interface{})
		if ok {
			if len(vals) == 0 {
				//fmt.Println("---------Key:", key)
			} else {
				fmt.Println("Key:", key, "Objs:", len(vals))
				for _, val := range vals {
					obj, _ := val.(map[string]interface{})
					if key == "FileObject" {
						var filePaths = make([]string, 0)
						var protoFilePath = "root.path"
						getFilePathFromData(protoFilePath, obj, &filePaths)
						if len(filePaths) != 0 {
							fmt.Println(filePaths)
						}
						fmt.Printf("\n")

					}
					/*
						if ok {
							count = count + 1
						}
						if uuidStr, ok := mVal["uuid"]; ok {
							_ = uuidStr
							if strings.ToLower(key) == "fileobject" {
								fmt.Println(mVal["type"])
								fmt.Println(mVal["checksum"])
								fmt.Println(mVal["type"].(string))

							}
							//fmt.Printf("%s ", uuidStr)
							fmt.Println(strings.SplitN("a.b.c", ",", -1))

						} else {
							//fmt.Println("=======================================uuid not present ", key)
							//fmt.Println(mVal)
						}
					*/
				}
			}
		} else {
			fmt.Println("----- did not cast ", key)
		}
	}
}

func getFilePathFromData(protoFilePath string, obj map[string]interface{}, filePaths *[]string) {
	newProtoFilePath := strings.SplitN(protoFilePath, ".", 2)
	if len(newProtoFilePath) == 2 {
		if newProtoFilePath[0] != "root" {
			if val, ok := obj[newProtoFilePath[0]]; ok {
				switch val.(type) {
				case map[string]interface{}:
					getFilePathFromData(newProtoFilePath[1], val.(map[string]interface{}), filePaths)
				case []interface{}:
					for _, v := range val.([]interface{}) {
						if mV, ok1 := v.(map[string]interface{}); ok1 {
							getFilePathFromData(newProtoFilePath[1], mV, filePaths)
						}
					}
				}
			}
		} else {
			getFilePathFromData(newProtoFilePath[1], obj, filePaths)
		}
	} else if len(newProtoFilePath) == 1 && newProtoFilePath[0] != "root" {
		if val, ok := obj[newProtoFilePath[0]]; ok {
			if mVal, ok1 := val.(string); ok1 {
				*filePaths = append(*filePaths, mVal)
			}
		}
	}
}
