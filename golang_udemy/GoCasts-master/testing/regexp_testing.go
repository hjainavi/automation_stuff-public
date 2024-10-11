package main

import (
	"fmt"
	"regexp"
)

var exportPattern = regexp.MustCompile(`(?m)^(.*\/export\/.*\/avi_backup\/.*\.json)`)

func main() {
	str1 := `Traceback (most recent call last):
  File "/opt/avi/scripts/task_journal_writer.py", line 55, in <module>
    raise Exception(log_taskjournal_obj.display_error)
Exception: Errors countered for ['fileobject'].
File '/var/lib/avi/other_files/admin/PXL_20240929_145756870.jpg' found for the object but file does not exist
For further details please refer to the upgrade journals.
/var/lib/avi/downloads/export/446097932/avi_backup/export_file.json`
	repl := "Journal export_file.json in ./avi_backup.tar.gz"
	fmt.Println(exportPattern.ReplaceAllLiteralString(str1, repl))
}
