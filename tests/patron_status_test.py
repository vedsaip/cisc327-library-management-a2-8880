import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tempfile
import pytest
from datetime import datetime, timedelta
from database import init_database, insert_book, insert_borrow_record
from library_service import get_patron_status_report

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
    
    assert "currently_borrowed" in report
    assert "total_late_fees" in report
    assert "num_borrowed" in report
    assert "borrow_history" in report
