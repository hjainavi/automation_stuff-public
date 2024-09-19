package main

import (
	"fmt"
	"regexp"
)

var EXPORT_BUNDLE_STR = "export_bundle"
var exportPattern = regexp.MustCompile(fmt.Sprintf(`.*\/%s(\d*)`, EXPORT_BUNDLE_STR))

func main() {
	str1 := "/home/aviuser/a/export_bundle3868276584/avi_backup/avi.tar.gz"
	fmt.Println(exportPattern.FindStringSubmatch(str1))
}
