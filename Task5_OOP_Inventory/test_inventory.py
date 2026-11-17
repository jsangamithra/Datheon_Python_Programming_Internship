"""Unit tests - run with:  python -m unittest -v   (inside this folder)"""
import unittest
from datetime import date, timedelta

from models import Book, DigitalMedia, Item, ItemUnavailableError, Magazine
from inventory import InventoryManager, InventoryError

TODAY = date(2026, 11, 17)


class TestModels(unittest.TestCase):
    def test_abstract_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Item("X", "x", 1)

    def test_price_validation(self):
        b = Book("B1", "T", 10, "A", 100)
        with self.assertRaises(ValueError):
            b.price = -1
        with self.assertRaises(TypeError):
            b.price = "x"

    def test_private_attribute_is_mangled(self):
        b = Book("B1", "T", 10, "A", 100)
        self.assertFalse(hasattr(b, "__price"))
        self.assertTrue(hasattr(b, "_Item__price"))

    def test_polymorphic_fees(self):
        for cls_args, days, expected in [
            (Book("B", "t", 42, "a", 1), 30, 4.5),              # 9 days * 0.50
            (Magazine("M", "t", 6, "i", "p"), 15, 2.0),          # 8 days * 0.25
            (DigitalMedia("D", "t", 9, 1, "MP4"), 20, 8.0),      # 2.00 + 6 * 1.00
        ]:
            cls_args.check_out("u", TODAY - timedelta(days=days))
            self.assertEqual(cls_args.calculate_fee(TODAY), expected)

    def test_equality_and_hash(self):
        a, b = Book("B1", "T", 1, "x", 1), Magazine("B1", "Other", 2, "i", "p")
        self.assertEqual(a, b)
        self.assertEqual(len({a, b}), 1)


class TestManager(unittest.TestCase):
    def setUp(self):
        self.m = InventoryManager()
        self.m.add(Book("B1", "Alpha", 10, "A", 10))

    def test_double_checkout(self):
        self.m.checkout("B1", "u", TODAY)
        with self.assertRaises(ItemUnavailableError):
            self.m.checkout("B1", "v", TODAY)

    def test_return_without_checkout(self):
        with self.assertRaises(InventoryError):
            self.m.return_item("B1", TODAY)

    def test_duplicate_id(self):
        with self.assertRaises(InventoryError):
            self.m.add(Book("B1", "Again", 1, "a", 1))


if __name__ == "__main__":
    unittest.main()
