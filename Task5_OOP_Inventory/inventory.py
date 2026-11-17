"""Task 5 (inventory.py) - InventoryManager + runnable demo.

Run:  python inventory.py
Writes the audit report to outputs/audit_report.txt and outputs/audit_report.csv
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

from models import (Book, DigitalMedia, InventoryError, Item,
                    ItemUnavailableError, Magazine)

OUT = Path(__file__).parent / "outputs"


class InventoryManager:
    """Handles catalogue, checkouts, returns and audit reporting."""

    def __init__(self) -> None:
        self._items: dict[str, Item] = {}
        self._history: list[tuple[str, str, str, str, float]] = []   # date, action, id, who, fee

    # container protocol -----------------------------------------------------
    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(sorted(self._items.values()))

    def __contains__(self, item_id: str) -> bool:
        return item_id in self._items

    # catalogue --------------------------------------------------------------
    def add(self, item: Item) -> None:
        if item.item_id in self._items:
            raise InventoryError(f"duplicate item id {item.item_id}")
        self._items[item.item_id] = item

    def get(self, item_id: str) -> Item:
        try:
            return self._items[item_id]
        except KeyError:
            raise InventoryError(f"unknown item id {item_id}") from None

    # transactions -----------------------------------------------------------
    def checkout(self, item_id: str, borrower: str, on: date | None = None) -> None:
        item = self.get(item_id)
        item.check_out(borrower, on)
        self._history.append((str(on or date.today()), "CHECKOUT", item_id, borrower, 0.0))

    def return_item(self, item_id: str, today: date | None = None) -> float:
        item = self.get(item_id)
        if item.is_available:
            raise InventoryError(f"'{item.title}' is not checked out")
        fee = item.calculate_fee(today)           # polymorphic call
        who = item.borrower or "?"
        item.check_in()
        self._history.append((str(today or date.today()), "RETURN", item_id, who, fee))
        return fee

    # reporting --------------------------------------------------------------
    def audit_rows(self, today: date | None = None) -> list[list[str]]:
        rows = []
        for it in self:
            rows.append([it.item_id, type(it).__name__, it.title,
                         "Available" if it.is_available else "Borrowed",
                         it.borrower or "-", str(it.days_borrowed(today)),
                         str(it.overdue_days(today)), f"{it.calculate_fee(today):.2f}",
                         f"{it.price:.2f}"])
        return rows

    HEADERS = ["ID", "Type", "Title", "Status", "Borrower", "Days", "Overdue", "Fee", "Price"]

    def audit_report(self, today: date | None = None) -> str:
        rows = [self.HEADERS] + self.audit_rows(today)
        widths = [max(len(r[i]) for r in rows) for i in range(len(self.HEADERS))]
        sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
        fmt = lambda r: "| " + " | ".join(c.ljust(w) for c, w in zip(r, widths)) + " |"
        lines = [sep, fmt(rows[0]), sep, *[fmt(r) for r in rows[1:]], sep]
        out = sum(1 for i in self if not i.is_available)
        fees = sum(i.calculate_fee(today) for i in self)
        lines.append(f"Items: {len(self)} | On loan: {out} | Available: {len(self) - out} "
                     f"| Outstanding fees: {fees:.2f}")
        return "\n".join(lines)

    def export_csv(self, path: Path, today: date | None = None) -> None:
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(self.HEADERS)
            w.writerows(self.audit_rows(today))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    today = date(2026, 11, 17)          # fixed date -> reproducible output
    lines: list[str] = []
    log = lambda s="": (print(s), lines.append(s))

    mgr = InventoryManager()
    mgr.add(Book("B001", "Clean Code", 42.00, "Robert C. Martin", 464))
    mgr.add(Book("B002", "Fluent Python", 55.00, "Luciano Ramalho", 1012))
    mgr.add(Magazine("M001", "Wired", 6.50, "Nov 2026", "Condé Nast"))
    mgr.add(Magazine("M002", "National Geographic", 7.00, "Oct 2026", "NatGeo Partners"))
    mgr.add(DigitalMedia("D001", "Python Masterclass", 19.99, 1450.5, "MP4"))
    mgr.add(DigitalMedia("D002", "Data Science Audiobook", 14.99, 320.0, "MP3"))

    log("=== 1. Catalogue (polymorphic display_metadata) ===")
    for it in mgr:
        log(f"{it}\n      {it.display_metadata()}")

    log("\n=== 2. Dunder methods ===")
    log(f"repr  : {mgr.get('B001')!r}")
    log(f"str   : {mgr.get('B001')}")
    log(f"len(manager) = {len(mgr)} items")
    log(f"Book('B001') == Book('B001') copy ? {mgr.get('B001') == Book('B001', 'X', 1, 'a', 1)}")

    log("\n=== 3. Checkouts ===")
    mgr.checkout("B001", "Alice", today - timedelta(days=30))   # 9 days overdue
    mgr.checkout("M001", "Bob", today - timedelta(days=15))     # 8 days overdue
    mgr.checkout("D001", "Carol", today - timedelta(days=20))   # 6 days overdue
    mgr.checkout("B002", "Dave", today - timedelta(days=5))     # on time
    log("4 checkouts recorded.")
    log(f"len(B001) = {len(mgr.get('B001'))} days borrowed (uses __len__)")

    log("\n=== 4. Error handling & validation ===")
    for label, action in [
        ("double checkout", lambda: mgr.checkout("B001", "Eve", today)),
        ("unknown id", lambda: mgr.get("Z999")),
        ("negative price", lambda: setattr(mgr.get("M002"), "price", -5)),
        ("string price", lambda: setattr(mgr.get("M002"), "price", "free")),
        ("return not borrowed", lambda: mgr.return_item("M002", today)),
    ]:
        try:
            action()
        except (InventoryError, ValueError, TypeError) as exc:
            log(f"{label:<20} -> {type(exc).__name__}: {exc}")

    log("\n=== 5. Audit report BEFORE returns ===")
    log(mgr.audit_report(today))

    log("\n=== 6. Returns (fee computed polymorphically) ===")
    for item_id in ("B001", "M001", "D001", "B002"):
        fee = mgr.return_item(item_id, today)
        log(f"Returned {item_id}: late fee = {fee:.2f}")

    log("\n=== 7. Audit report AFTER returns ===")
    log(mgr.audit_report(today))

    (OUT / "audit_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    mgr.export_csv(OUT / "audit_report.csv", today)
    print(f"\nSaved: {OUT / 'audit_report.txt'} and audit_report.csv")


if __name__ == "__main__":
    main()
