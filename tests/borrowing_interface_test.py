import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tempfile
import pytest
from database import init_database, insert_book, get_book_by_isbn, get_patron_borrowed_books
from library_service import borrow_book_by_patron

@pytest.fixture(autouse=True)
def setup_and_teardown_db(monkeypatch):
    db_fd, temp_db = tempfile.mkstemp()
    monkeypatch.setattr("database.DATABASE", temp_db)
    init_database()
    yield
    os.close(db_fd)
    os.unlink(temp_db)

def test_patron_can_borrow_book():
    insert_book("Test Book", "Author", "1234567899999", 2, 2)
    book = get_book_by_isbn("1234567899999")

    success, message = borrow_book_by_patron("123456", book["id"])
    assert success is True
    assert "successfully borrowed" in message.lower()

    borrowed = get_patron_borrowed_books("123456")
    assert len(borrowed) == 1
    assert borrowed[0]["book_id"] == book["id"]

def test_invalid_patron_id_rejected():
    # Test non-6-digit IDs
    insert_book("Test Book", "Author", "1234567899999", 1, 1)
    book = get_book_by_isbn("1234567899999")
    
    success, message = borrow_book_by_patron("12345", book["id"])  # 5 digits
    assert success is False
    assert "invalid patron id" in message.lower()

def test_borrowing_limit_enforced():
    # Set up patron with 5 books already borrowed
    # Then try to borrow a 6th book
    pass

def test_unavailable_book_rejected():
    insert_book("Test Book", "Author", "1234567899999", 1, 0)  # 0 available
    book = get_book_by_isbn("1234567899999")
    
    success, message = borrow_book_by_patron("123456", book["id"])
    assert success is False
