# Datheon Python Programming Internship

A portfolio of four Python 3 projects (standard library only, no external dependencies), each in its own folder with source code, a README and real run outputs.

| Task | Project | Difficulty | Key concepts | Folder |
|------|---------|-----------|--------------|--------|
| 1 | Hangman Word Guessing Game | Beginner | strings, sets, `random`, control flow, ASCII art | [`Task1_Hangman`](Task1_Hangman) |
| 3 | Automated File Organizer & Cleanup Utility | Intermediate | `os`, `shutil`, `pathlib`, exceptions, logging | [`Task3_File_Organizer`](Task3_File_Organizer) |
| 4 | Rule-Based Terminal Chatbot | Beginner | `re`, `json`, state machine, multi-intent matching | [`Task4_Chatbot`](Task4_Chatbot) |
| 5 | OOP Smart Inventory & Asset System | Intermediate | ABCs, inheritance, polymorphism, encapsulation, dunder methods | [`Task5_OOP_Inventory`](Task5_OOP_Inventory) |

## Repository structure

```
Datheon_Python_Programming_Internship/
├── README.md
├── .gitignore
├── Task1_Hangman/
│   ├── hangman.py
│   ├── words.txt
│   ├── README.md
│   └── outputs/demo_run.txt
├── Task3_File_Organizer/
│   ├── organizer.py
│   ├── README.md
│   └── outputs/{demo_run.txt, organizer.log, final_tree.txt}
├── Task4_Chatbot/
│   ├── chatbot.py
│   ├── faq.json
│   ├── README.md
│   └── outputs/demo_run.txt
└── Task5_OOP_Inventory/
    ├── models.py
    ├── inventory.py
    ├── test_inventory.py
    ├── README.md
    └── outputs/{demo_run.txt, audit_report.txt, audit_report.csv, test_results.txt}
```

## Requirements

* Python 3.10 or newer (developed on 3.13). Nothing to install.

## Quick start

```bash
git clone https://github.com/<your-username>/Datheon_Python_Programming_Internship.git
cd Datheon_Python_Programming_Internship

python Task1_Hangman/hangman.py            # play interactively  (add --demo for a scripted run)
python Task3_File_Organizer/organizer.py ~/Downloads --dry-run   # preview, then run without --dry-run
python Task4_Chatbot/chatbot.py            # chat interactively  (add --demo for a scripted run)
cd Task5_OOP_Inventory && python inventory.py && python -m unittest -v
```

Each task folder has an `outputs/` directory with the saved results of a real run, so reviewers can see the behaviour without running anything.

## Author

Submitted for the Datheon Python Programming Internship.
