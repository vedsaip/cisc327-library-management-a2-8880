import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tempfile
import pytest
from database import init_database, insert_book
from library_service import search_books_in_catalog

@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    db_fd, temp_db = tempfile.mkstemp()
    monkeypatch.setattr("database.DATABASE", temp_db)
    init_database()
    yield
    os.close(db_fd)
    os.unlink(temp_db)

def test_search_by_title_partial():
    insert_book("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "1234567890001", 1, 1)
    
    results = search_books_in_catalog("harry potter", "title")
    assert len(results) > 0
    assert "Harry Potter" in results[0]["title"]

def test_search_by_author_case_insensitive():
    insert_book("Test Book", "Some Author", "1234567890002", 1, 1)
    results = search_books_in_catalog("some author", "author")
    assert len(results) > 0
    assert "Some Author" == results[0]["author"]

def test_search_by_isbn_exact():
    insert_book("Exact ISBN Book", "Author", "9999999999999", 1, 1)
    results = search_books_in_catalog("9999999999999", "isbn")
    assert len(results) == 1
    assert results[0]["isbn"] == "9999999999999"
