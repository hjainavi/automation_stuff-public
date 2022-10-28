package main

import (
	"fmt"
	"net/url"
	"path/filepath"
	"regexp"
	"strings"
)

func main() {
	uri := "/api/cloud/ladskjflkajf"
	fmt.Println(strings.ContainsAny(uri, "./"))
	fmt.Println(modelSlugFromUri(uri))
	//o, _ := url.Parse(uri)
	//r, _ := regexp.Compile(`name=(?P<name>.+)`)

	//fmt.Printf("%#v\n", r.MatchString(o.RawQuery))
	//q, _ := url.QueryUnescape(o.RawQuery)
	//fmt.Printf("%#v\n", getRegexParams(r, q))

}

func getRegexParams(compRegEx *regexp.Regexp, url string) (paramsMap map[string]string) {
	match := compRegEx.FindStringSubmatch(url)

	paramsMap = make(map[string]string)
	for i, name := range compRegEx.SubexpNames() {
		if i > 0 && i <= len(match) {
			paramsMap[name] = match[i]
		}
	}
	return paramsMap
}

func modelSlugFromUri(uri string) (string, string) {
	obj, err := url.Parse(uri)
	if err != nil {
		return "", uri
	}

	escapedPath := obj.EscapedPath()
	slug := filepath.Base(escapedPath)
	if strings.Contains(slug, "#") {
		slug = strings.Split(slug, "#")[0]
	}
	model := slug
	model = strings.ToLower(filepath.Base(filepath.Dir(escapedPath)))
	if slug == "." {
		return "", uri
	}
	return model, slug
}
