package main

import (
	"fmt"
	"net/url"
	"path/filepath"
	"regexp"
	"strings"
)

func fixProtocol(uri string) string {
	// fix for issues with url parser
	match, _ := regexp.MatchString("^https?://", uri)
	if !(strings.HasPrefix(uri, "/") || match) {
		uri = "http://" + uri
	}
	return uri
}

var globalApiList = [...]string{"ControllerProperties", "LicenseStatus", "ALBServicesConfig", "SystemConfiguration", "SeProperties", "ControllerLicense", "CloudProperties", "LicenseLedgerDetails", "SystemLimits", "InventoryFaultConfig"}

func isGlobalApi(objType string) bool {
	for _, v := range globalApiList {
		if strings.ToLower(v) == strings.ToLower(objType) {
			return true
		}
	}
	return false
}

func modelSlugFromUri(uri string) (string, string) {
	obj, err := url.Parse(fixProtocol(uri))
	if err != nil {
		fmt.Println("url parse error: ", err)
		return "", uri
	}
	fmt.Println("obj = ", obj)
	escapedPath := obj.EscapedPath()
	fmt.Println("escapedPath = ", escapedPath)
	slug := filepath.Base(escapedPath)
	fmt.Println("slug = ", slug)
	if strings.Contains(slug, "#") {
		slug = strings.Split(slug, "#")[0]
	}
	fmt.Println("slug = ", slug)
	model := slug
	if !isGlobalApi(slug) {
		model = strings.ToLower(filepath.Base(filepath.Dir(escapedPath)))
	}
	fmt.Println("model = ", model, ", slug = ", slug)
	if slug == "." {
		fmt.Println("url parse error, defaulting to original uri")
		return "", uri
	}
	fmt.Println("model = ", model, ", slug = ", slug)
	return model, slug
}

func main() {
	uri := "https://100.65.9.183/api/pool/pool-uuid/?fields=uuid"
	fmt.Println(modelSlugFromUri(uri))
}
