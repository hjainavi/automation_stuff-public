package main

import (
	"fmt"

	"gopkg.in/yaml.v2"
)

func main() {
	YamlTesting()
}

var yamlData = `
ConfigChecker:
  description: Validates the exported configuration
  file: /opt/avi/log/task_journal/upgrade_config_checker.json
  process_type: ConfigChecker
ImportConfig:
  description: Configuration Import
  file: /opt/avi/log/task_journal/upgrade_import_config.json
  process_type: ImportConfig
InitialDataImport:
  description: Initial Data Import
  file: /opt/avi/log/task_journal/upgrade_initial_data.json
  process_type: InitialDataImport
MigrateConfig:
  description: Config Migration
  file: /opt/avi/log/task_journal/upgrade_migrate_config.json
  process_type: MigrateConfig
ExportFile:
  description: File Export
  file: /opt/avi/log/task_journal/upgrade_export_file.json
  process_type: ExportFile
`

func YamlTesting() {

	mainY := make(map[string]map[string]string)
	/*
		mainY := struct {
			ModelFiles map[string]struct {
				Path string `yaml:"path"`
			} `yaml:"model_files"`
			ErrorHandling struct {
				RaiseErrorOnFileExport   bool `yaml:"raise_error_on_file_export"`
				RaiseErrorOnConfigExport bool `yaml:"raise_error_on_config_export"`
			} `yaml:"error_handling"`
		}{}
	*/
	err := yaml.Unmarshal([]byte(yamlData), &mainY)
	if err != nil {
		fmt.Println("222: ", err)
	}
	fmt.Printf("%+v\n", mainY["ConfigChecker"]["file"])
	fmt.Printf("%+v\n", mainY["ExportFile"]["file"])

}
