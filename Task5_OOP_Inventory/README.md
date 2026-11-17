# Task 5 - OOP Architecture: Enterprise Smart Inventory & Asset System

A modular object-oriented system for tracking library/enterprise assets.

## Run

```bash
python inventory.py          # runs the full demo, writes outputs/
python -m unittest -v        # 8 unit tests
```

## OOP concepts and where to find them

| Concept | Implementation |
|---------|----------------|
| Abstraction | `Item(ABC)` in `models.py` with abstract `calculate_fee()`, `display_metadata()` and `loan_period_days` |
| Inheritance | `Book`, `Magazine`, `DigitalMedia` extend `Item` and call `super().__init__()` |
| Polymorphism | `InventoryManager.return_item()` calls `item.calculate_fee()` on any subclass |
| Encapsulation | private `__price` and `__borrow_date`, accessed through `@property` / `@setter` with validation |
| Dunder methods | `__str__`, `__repr__`, `__len__` (days borrowed), `__eq__`, `__hash__`, `__lt__` (sorting); manager has `__len__`, `__iter__`, `__contains__` |
| Custom exceptions | `InventoryError`, `ItemUnavailableError` |

## Late fee rules

| Type | Loan period | Fee |
|------|-------------|-----|
| Book | 21 days | 0.50/day, capped at the book's price |
| Magazine | 7 days | 0.25/day |
| DigitalMedia | 14 days | 2.00 flat + 1.00/day once overdue |

The brief names the abstract class `LibraryItem`, while the suggested approach calls it `Item`. This project uses `Item`; a one-line alias (`LibraryItem = Item`) can be added if you want both names.

## Outputs

* [`outputs/demo_run.txt`](outputs/demo_run.txt) - full console run
* [`outputs/audit_report.txt`](outputs/audit_report.txt) - tabular audit report (before and after returns)
* [`outputs/audit_report.csv`](outputs/audit_report.csv) - CSV export
* [`outputs/test_results.txt`](outputs/test_results.txt) - unit test results
