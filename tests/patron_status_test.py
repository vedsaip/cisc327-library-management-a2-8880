import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tempfile
import pytest
from datetime import datetime, timedelta
from database import init_database, insert_book, insert_borrow_record
from services.library_service import get_patron_status_report

@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    db_fd, temp_db = tempfile.mkstemp()
    monkeypatch.setattr("database.DATABASE", temp_db)
    init_database()
    yield
    os.close(db_fd)
    os.unlink(temp_db)

def test_patron_status_report_fields():
    insert_book("History Book", "Author", "1234567890003", 1, 1)
    borrow_date = datetime.now() - timedelta(days=2)
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record("123456", 1, borrow_date, due_date)
    
    report = get_patron_status_report("123456")
    
    assert "patron_id" in report
    assert "borrowed_books" in report  
    assert "total_books_borrowed" in report  
    assert "total_late_fees" in report  
    assert "status" in report  
    
    # Verify the values make sense
    assert report["patron_id"] == "123456"
    assert report["total_books_borrowed"] == 1
    assert isinstance(report["borrowed_books"], list)
    assert len(report["borrowed_books"]) == 1
