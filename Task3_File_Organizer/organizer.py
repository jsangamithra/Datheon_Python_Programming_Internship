"""Task 3 - Automated File Organizer & Cleanup Utility.

Sorts files in a directory into category sub-folders by extension.

Safety features
---------------
* --dry-run previews every move without touching the disk.
* Naming collisions are resolved by appending _1, _2, ... (nothing is overwritten).
* PermissionError / OSError are caught per file and reported, never crash the run.
* Every action is written to a log file and to the console.

Usage
-----
    python organizer.py /path/to/Downloads
    python organizer.py /path/to/Downloads --dry-run
    python organizer.py --demo            # builds a messy sandbox folder and organises it
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

CATEGORY_MAP = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"},
    "Images":    {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"},
    "Videos":    {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Audio":     {".mp3", ".wav", ".flac", ".aac", ".ogg"},
    "Archives":  {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code":      {".py", ".js", ".ts", ".java", ".c", ".cpp", ".html", ".css", ".json", ".sql", ".sh"},
}
EXT_TO_CATEGORY = {ext: cat for cat, exts in CATEGORY_MAP.items() for ext in exts}
OTHER = "Others"
LOG_NAME = "organizer.log"

log = logging.getLogger("organizer")


def setup_logging(log_file: Path) -> None:
    log.setLevel(logging.INFO)
    log.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    for handler in (logging.StreamHandler(sys.stdout), logging.FileHandler(log_file, "w", encoding="utf-8")):
        handler.setFormatter(fmt)
        log.addHandler(handler)


def category_for(path: Path) -> str:
    return EXT_TO_CATEGORY.get(path.suffix.lower(), OTHER)


def unique_destination(dest: Path) -> Path:
    """Return a non-existing path: report.pdf -> report_1.pdf -> report_2.pdf ..."""
    if not dest.exists():
        return dest
    counter = 1
    while True:
        candidate = dest.with_name(f"{dest.stem}_{counter}{dest.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize(source: Path, dry_run: bool = False) -> dict:
    stats = {"moved": Counter(), "renamed": 0, "errors": 0, "skipped": 0}
    category_dirs = set(CATEGORY_MAP) | {OTHER}

    with os.scandir(source) as entries:
        files = sorted((Path(e.path) for e in entries if e.is_file(follow_symlinks=False)),
                       key=lambda p: p.name.lower())

    for file in files:
        if file.name == LOG_NAME or file.name.startswith("."):
            stats["skipped"] += 1
            continue
        category = category_for(file)
        target_dir = source / category
        try:
            if not dry_run:
                target_dir.mkdir(exist_ok=True)           # dynamic folder creation
            dest = unique_destination(target_dir / file.name)
            if dest.name != file.name:
                stats["renamed"] += 1
            if dry_run:
                log.info("[DRY-RUN] %s -> %s/%s", file.name, category, dest.name)
            else:
                shutil.move(str(file), str(dest))
                log.info("MOVED   %s -> %s/%s", file.name, category, dest.name)
            stats["moved"][category] += 1
        except PermissionError as exc:
            stats["errors"] += 1
            log.error("PERMISSION DENIED for %s (%s)", file.name, exc)
        except FileExistsError as exc:
            stats["errors"] += 1
            log.error("FILE EXISTS for %s (%s)", file.name, exc)
        except OSError as exc:
            stats["errors"] += 1
            log.error("OS ERROR for %s (%s)", file.name, exc)
    return stats


def print_summary(stats: dict, dry_run: bool) -> None:
    total = sum(stats["moved"].values())
    log.info("=" * 46)
    log.info("EXECUTION SUMMARY %s", "(DRY RUN - nothing moved)" if dry_run else "")
    log.info("=" * 46)
    log.info("%-14s %s", "Category", "Files")
    log.info("-" * 22)
    for cat, n in sorted(stats["moved"].items()):
        log.info("%-14s %d", cat, n)
    log.info("-" * 22)
    log.info("Total relocated : %d", total)
    log.info("Renamed (collision): %d", stats["renamed"])
    log.info("Skipped         : %d", stats["skipped"])
    log.info("Errors          : %d", stats["errors"])


def build_demo_folder(root: Path) -> None:
    """Create a cluttered sandbox, including a deliberate naming collision."""
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    names = ["resume.pdf", "notes.txt", "budget.xlsx", "photo1.jpg", "logo.PNG", "banner.png",
             "trailer.mp4", "lecture.mkv", "backup.zip", "dataset.tar", "script.py", "app.js",
             "song.mp3", "setup.exe", "mystery_file", "report.pdf"]
    for n in names:
        (root / n).write_text(f"demo content of {n}\n")
    # Collision: pre-existing Documents/report.pdf forces report_1.pdf
    (root / "Documents").mkdir()
    (root / "Documents" / "report.pdf").write_text("older report\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Organise a cluttered folder by file type.")
    parser.add_argument("directory", nargs="?", help="folder to organise")
    parser.add_argument("--dry-run", action="store_true", help="preview only")
    parser.add_argument("--demo", action="store_true", help="create sandbox and organise it")
    args = parser.parse_args()

    if args.demo:
        source = Path(__file__).parent / "demo_sandbox"
        build_demo_folder(source)
        print(f"Created demo folder: {source}\n")
    elif args.directory:
        source = Path(args.directory).expanduser().resolve()
    else:
        parser.error("provide a directory or use --demo")

    if not source.is_dir():
        sys.exit(f"Error: '{source}' is not a directory.")

    outputs = Path(__file__).parent / "outputs"
    outputs.mkdir(exist_ok=True)
    setup_logging(outputs / LOG_NAME if args.demo else source / LOG_NAME)
    stats = organize(source, dry_run=args.dry_run)
    print_summary(stats, args.dry_run)

    if args.demo:
        tree = ["", "Final folder tree:"]
        for p in sorted(source.rglob("*")):
            tree.append("  " + str(p.relative_to(source)) + ("/" if p.is_dir() else ""))
        text = "\n".join(tree)
        print(text)
        (outputs / "final_tree.txt").write_text(text.strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
