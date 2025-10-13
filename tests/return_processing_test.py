import os
import tempfile
import pytest
from datetime import datetime, timedelta
from database import init_database, insert_book, insert_borrow_record, get_book_by_id, get_patron_borrowed_books
from library_service import return_book_by_patron

@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    db_fd, temp_db = tempfile.mkstemp()
    monkeypatch.setattr("database.DATABASE", temp_db)
    init_database()
    yield
    os.close(db_fd)
    os.unlink(temp_db)

def test_return_book_updates_availability():
    insert_book("Return Test", "Author", "1234567890123", 1, 0)
    book = get_book_by_id(1)
    
    borrow_date = datetime.now() - timedelta(days=5)
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record("123456", book["id"], borrow_date, due_date)
    
    success, message = return_book_by_patron("123456", book["id"])
    
    assert success is True
    assert "returned" in message.lower()
    
    updated_book = get_book_by_id(book["id"])
    assert updated_book["available_copies"] == 1
