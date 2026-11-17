# Task 3 - Automated File Organizer & Cleanup Utility

Sorts a cluttered folder (e.g. Downloads) into `Documents`, `Images`, `Videos`, `Audio`, `Archives`, `Code` and `Others`.

## Run

```bash
python organizer.py ~/Downloads --dry-run   # preview only, nothing moves
python organizer.py ~/Downloads             # do it (writes organizer.log into that folder)
python organizer.py --demo                  # builds a sandbox, organises it, saves outputs/
```

## How it works

1. `os.scandir()` lists the files in the target directory (sub-folders are left alone).
2. The extension is looked up (case-insensitive) in a category dictionary; unknown types go to `Others`.
3. Category folders are created on demand.
4. `shutil.move()` relocates the file. If the name already exists, the file becomes `name_1.ext`, `name_2.ext`, and so on. Nothing is overwritten.
5. `PermissionError`, `FileExistsError` and other `OSError`s are caught per file, logged, and counted without stopping the run.
6. A formatted summary (per-category counts, renamed, skipped, errors) is printed and logged.

## Outputs

* [`outputs/demo_run.txt`](outputs/demo_run.txt) - console output of the demo
* [`outputs/organizer.log`](outputs/organizer.log) - the log file
* [`outputs/final_tree.txt`](outputs/final_tree.txt) - folder tree after organising (note `report.pdf` and `report_1.pdf`, the collision handling)
