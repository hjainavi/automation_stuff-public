package main

import (
	"fmt"
	"reflect"
	"strings"
)

type ApiKwargs struct {
	Model                         string
	Scoped                        bool
	ScopeVisible                  bool
	AllowAllTenants               bool
	AllowAny                      bool
	SkipVersioning                bool
	SkipCreateSystemDefaultObject bool
	Name                          string
	Slug                          string
	Key                           string
	Tenant                        string
	Cloud                         string
	Version                       string
	LicenseTier                   string
	ForceDelete                   bool
	MacroRequestInternal          string
	MacroRequestInternalChildKey  string
	AsyncRequest                  bool
	SystemDefault                 bool
}

func main() {
	x := &ApiKwargs{Model: "testmodel", Scoped: true}
	x_map := map[string]string{"cloud": "abc_cloud", "forcedelete": "true"}

	v_val := reflect.ValueOf(x)
	v_type := reflect.TypeOf(*x)

	for i := 0; i < v_type.NumField(); i++ {
		for key, val := range x_map {
			if strings.ToLower(v_type.Field(i).Name) == strings.ToLower(key) {
				f := v_val.Elem().FieldByName(v_type.Field(i).Name)
				if f.Kind() == reflect.Bool {
					if val == "true" {
						f.SetBool(true)
					}
					if val == "false" {
						f.SetBool(false)
					}
				}
				if f.Kind() == reflect.String {
					f.SetString(val)
				}
			}
		}
	}

	fmt.Printf("%+v", x)
}
