import os
import tempfile
import pytest
from datetime import datetime, timedelta
from database import init_database, insert_book, insert_borrow_record
from library_service import calculate_late_fee_for_book

@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    db_fd, temp_db = tempfile.mkstemp()
    monkeypatch.setattr("database.DATABASE", temp_db)
    init_database()
    yield
    os.close(db_fd)
    os.unlink(temp_db)

def test_late_fee_calculation():
    insert_book("Late Book", "Author", "1234567890999", 1, 1)
    borrow_date = datetime.now() - timedelta(days=20)  # 6 days overdue for first week
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record("123456", 1, borrow_date, due_date)
    
    result = calculate_late_fee_for_book("123456", 1)
    
    assert "fee_amount" in result
    assert "days_overdue" in result
    assert result["days_overdue"] == 6
    assert result["fee_amount"] > 0
