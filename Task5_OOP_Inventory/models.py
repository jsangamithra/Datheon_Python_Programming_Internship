"""Task 5 (models.py) - Domain model for the Enterprise Smart Inventory & Asset System.

OOP concepts demonstrated
-------------------------
* Abstraction     : Item(ABC) with @abstractmethod calculate_fee() and display_metadata()
* Inheritance     : Book, Magazine, DigitalMedia extend Item
* Polymorphism    : each subclass overrides calculate_fee() / display_metadata()
* Encapsulation   : private attributes (__price, __borrow_date, ...) behind @property
* Dunder methods  : __str__, __repr__, __len__, __eq__, __hash__, __lt__
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, timedelta


class InventoryError(Exception):
    """Base error for the inventory domain."""


class ItemUnavailableError(InventoryError):
    pass


class Item(ABC):
    """Abstract base class (the brief calls it LibraryItem; 'Item' is used in the suggested approach)."""

    _registry_count = 0          # class-level counter (shared state)

    def __init__(self, item_id: str, title: str, price: float):
        self._item_id = item_id          # protected (read-only through property)
        self._title = title
        self.__price = 0.0               # private (name-mangled)
        self.__borrow_date: date | None = None
        self.__borrower: str | None = None
        self.price = price               # goes through the validating setter
        Item._registry_count += 1

    # ---------- encapsulated attributes ----------
    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError("price must be a number")
        if value < 0:
            raise ValueError("price cannot be negative")
        self.__price = round(float(value), 2)

    @property
    def borrow_date(self) -> date | None:
        return self.__borrow_date

    @borrow_date.setter
    def borrow_date(self, value: date | None) -> None:
        if value is not None and value > date.today() + timedelta(days=1):
            raise ValueError("borrow date cannot be in the future")
        self.__borrow_date = value

    @property
    def borrower(self) -> str | None:
        return self.__borrower

    @property
    def is_available(self) -> bool:
        return self.__borrow_date is None

    # ---------- behaviour ----------
    def check_out(self, borrower: str, on: date | None = None) -> None:
        if not self.is_available:
            raise ItemUnavailableError(f"'{self.title}' is already borrowed by {self.__borrower}")
        self.borrow_date = on or date.today()
        self.__borrower = borrower

    def check_in(self) -> None:
        self.__borrow_date = None
        self.__borrower = None

    def days_borrowed(self, today: date | None = None) -> int:
        if self.__borrow_date is None:
            return 0
        return max(((today or date.today()) - self.__borrow_date).days, 0)

    # ---------- abstract interface ----------
    @property
    @abstractmethod
    def loan_period_days(self) -> int: ...

    @abstractmethod
    def calculate_fee(self, today: date | None = None) -> float:
        """Late fee owed right now."""

    @abstractmethod
    def display_metadata(self) -> str:
        """One-line description specific to the subclass."""

    def overdue_days(self, today: date | None = None) -> int:
        return max(self.days_borrowed(today) - self.loan_period_days, 0)

    # ---------- dunder methods ----------
    def __str__(self) -> str:
        status = "Available" if self.is_available else f"Borrowed by {self.borrower}"
        return f"[{self.item_id}] {self.title} ({type(self).__name__}) - {status}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(item_id={self.item_id!r}, title={self.title!r}, price={self.price})"

    def __len__(self) -> int:
        """len(item) = days currently borrowed (0 if on the shelf)."""
        return self.days_borrowed()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Item) and self.item_id == other.item_id

    def __hash__(self) -> int:
        return hash(self.item_id)

    def __lt__(self, other: "Item") -> bool:
        return self.title.lower() < other.title.lower()


class Book(Item):
    FEE_PER_DAY = 0.50

    def __init__(self, item_id: str, title: str, price: float, author: str, pages: int):
        super().__init__(item_id, title, price)
        self.author = author
        self.pages = pages

    @property
    def loan_period_days(self) -> int:
        return 21

    def calculate_fee(self, today: date | None = None) -> float:
        # capped at the replacement price of the book
        return round(min(self.overdue_days(today) * self.FEE_PER_DAY, self.price), 2)

    def display_metadata(self) -> str:
        return f"Author: {self.author} | Pages: {self.pages}"


class Magazine(Item):
    FEE_PER_DAY = 0.25

    def __init__(self, item_id: str, title: str, price: float, issue: str, publisher: str):
        super().__init__(item_id, title, price)
        self.issue = issue
        self.publisher = publisher

    @property
    def loan_period_days(self) -> int:
        return 7

    def calculate_fee(self, today: date | None = None) -> float:
        return round(self.overdue_days(today) * self.FEE_PER_DAY, 2)

    def display_metadata(self) -> str:
        return f"Issue: {self.issue} | Publisher: {self.publisher}"


class DigitalMedia(Item):
    FLAT_FEE = 2.00
    FEE_PER_DAY = 1.00

    def __init__(self, item_id: str, title: str, price: float, file_size_mb: float, fmt: str):
        super().__init__(item_id, title, price)
        self.file_size_mb = file_size_mb
        self.format = fmt

    @property
    def loan_period_days(self) -> int:
        return 14

    def calculate_fee(self, today: date | None = None) -> float:
        late = self.overdue_days(today)
        return round(self.FLAT_FEE + late * self.FEE_PER_DAY, 2) if late else 0.0

    def display_metadata(self) -> str:
        return f"Format: {self.format} | Size: {self.file_size_mb} MB"
