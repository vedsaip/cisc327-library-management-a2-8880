import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from library_service import add_book_to_catalog

def test_add_valid_book(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_isbn", lambda isbn: None)
    monkeypatch.setattr("library_service.insert_book", lambda *args, **kwargs: True)

    success, msg = add_book_to_catalog("Good Title", "Author A", "1234567890123", 3)
    assert success is True
    assert "successfully" in msg.lower()

def test_add_book_missing_title():
    success, msg = add_book_to_catalog("", "Author A", "1234567890123", 2)
    assert success is False
    assert "title is required" in msg.lower()

def test_add_book_invalid_isbn(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_isbn", lambda isbn: None)
    success, msg = add_book_to_catalog("Book", "Author", "123", 1)
    assert success is False
    assert "isbn must be exactly 13 digits" in msg.lower()

def test_add_book_duplicate_isbn(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_isbn", lambda isbn: {"id": 1})
    success, msg = add_book_to_catalog("Book", "Author", "1234567890123", 2)
    assert success is False
    assert "already exists" in msg.lower()
