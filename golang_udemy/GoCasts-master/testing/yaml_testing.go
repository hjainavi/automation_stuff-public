package main

import (
	"fmt"
	"os"
	"time"

	"gopkg.in/yaml.v2"
)

func main() {
	/*
		_, patch, mainV, build, _ := Version()
		fmt.Printf("%+v\n", mainV)
		fmt.Printf("%+v\n", build)
		if patch == "" {
			fmt.Println("NIL VAL")
		}
		fmt.Printf("%+v", patch)
		fmt.Println(GetTimeStampNow())
	*/
	YamlTesting()

}

func GetTimeStampNow() (formatted_timestamp string) {
	t := time.Now()
	// Required for CLI representation
	formatted_timestamp = t.Format("2006-01-02 15:04:05")

	return formatted_timestamp
}

func Version() (string, string, string, string, error) {
	const mainVersionFile = "/home/aviuser/VERSION"
	const patchVersionFile = "/home/aviuser/PATCH_VERSION"
	mainVersionBytes, err := os.ReadFile(mainVersionFile)
	if err != nil {
		return "", "", "", "", err
	}
	mainVersion := &struct {
		Version string `yaml:"Version"`
		Build   string `yaml:"build"`
	}{}

	err = yaml.Unmarshal(mainVersionBytes, mainVersion)
	if err != nil {
		return "", "", "", "", err
	}
	patchVersionBytes, err := os.ReadFile(patchVersionFile)
	if err != nil {
		return "", "", "", "", err
	}
	patchVersion := &struct {
		Patch string `yaml:"patch"`
	}{}
	err = yaml.Unmarshal(patchVersionBytes, patchVersion)
	if err != nil {
		return "", "", "", "", err
	}

	return fmt.Sprintf("%v", *mainVersion), patchVersion.Patch, mainVersion.Version, mainVersion.Build, nil
}

func YamlTesting() {
	yamlFile := "/home/aviuser/test.yml"
	valueBytes, err := os.ReadFile(yamlFile)
	if err != nil {
		fmt.Println("111: ", err)
	}
	mainY := struct {
		ModelFiles map[string]struct {
			Path string `yaml:"path"`
		} `yaml:"model_files"`
		ErrorHandling struct {
			RaiseErrorOnFileExport   bool `yaml:"raise_error_on_file_export"`
			RaiseErrorOnConfigExport bool `yaml:"raise_error_on_config_export"`
		} `yaml:"error_handling"`
	}{}
	err = yaml.Unmarshal(valueBytes, &mainY)
	if err != nil {
		fmt.Println("222: ", err)
	}
	fmt.Printf("%+v\n", mainY)
	for modelName, pathStruct := range mainY.ModelFiles {
		fmt.Println(modelName, pathStruct.Path)
	}
	dname, err := os.MkdirTemp("", "sampledir")
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("Temp dir name:", dname)
	os.RemoveAll(dname + "11")
}
