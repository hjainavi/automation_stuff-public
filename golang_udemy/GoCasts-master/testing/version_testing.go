package main

import (
	"fmt"
	"sort"
	"strings"

	version "github.com/hashicorp/go-version"
)

func abc() error {
	var err error
	var v *version.Version
	fmt.Println("---")
	fieldIntroducedIn := "abc--, "
	versionListStr := strings.Split(strings.Replace(fieldIntroducedIn, " ", "", -1), ",")
	fmt.Printf("%+v\n", versionListStr)
	versionCollection := version.Collection{}
	for _, val := range versionListStr {
		v, err = version.NewVersion(val)
		if err != nil {
			fmt.Println(err)
			continue
		}
		versionCollection = append(versionCollection, v)
	}
	fmt.Println(val)
	if len(versionCollection) == 0 {
		fmt.Println("here")
		fmt.Println(err)
		return err
	}
	sort.Sort(versionCollection)
	fmt.Println(versionCollection)
	return nil
}

func main() {
	fmt.Println("===========", abc())
}
