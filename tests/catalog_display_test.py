import os
import tempfile
import pytest
from database import init_database, get_book_by_isbn
from library_service import add_book_to_catalog

@pytest.fixture(autouse=True)
def setup_and_teardown_db(monkeypatch):
    """Set up a temporary database for testing and tear it down after."""
    db_fd, temp_db = tempfile.mkstemp()
    monkeypatch.setattr("database.DATABASE", temp_db)  # redirect DB to temp file
    init_database()
    yield
    os.close(db_fd)
    os.unlink(temp_db)


def test_add_new_unique_book():
    """Test adding a book with a unique ISBN succeeds."""
    success, message = add_book_to_catalog("New Book", "Some Author", "9999999999999", 2)
    assert success is True
    assert "success" in message.lower()
    # Check directly in DB
    book = get_book_by_isbn("9999999999999")
    assert book is not None
    assert book["title"] == "New Book"


def test_add_duplicate_book():
    """Test adding a duplicate book with same ISBN fails."""
    # First add succeeds
    success, message = add_book_to_catalog("Book A", "Author A", "1111111111111", 3)
    assert success is True

    # Second add with same ISBN fails
    success, message = add_book_to_catalog("Book A - Copy", "Author A", "1111111111111", 3)
    assert success is False
    assert "already exists" in message.lower()
