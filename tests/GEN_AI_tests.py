"""
Test Suite for Library Management System
Tests all functionalities (R1-R7) with comprehensive test cases
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import os
from datetime import datetime, timedelta
from database import init_database, get_db_connection, DATABASE
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report
)


class TestLibraryService(unittest.TestCase):
    """Test cases for Library Management System"""
    
    def setUp(self):
        """Set up fresh database before each test"""
        # Remove existing test database if it exists
        if os.path.exists('test_library.db'):
            os.remove('test_library.db')
        
        # Modify the DATABASE variable in the database module
        import database
        database.DATABASE = 'test_library.db'
        
        # Initialize fresh database
        init_database()
        
    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists('test_library.db'):
            os.remove('test_library.db')


class TestR1_AddBookToCatalog(TestLibraryService):
    """Test R1: Book Catalog Management - add_book_to_catalog"""
    
    def test_add_valid_book(self):
        """Test adding a valid book to catalog"""
        success, message = add_book_to_catalog(
            "The Catcher in the Rye",
            "J.D. Salinger",
            "9780316769175",
            3
        )
        self.assertTrue(success)
        self.assertIn("successfully added", message)
    
    def test_add_book_empty_title(self):
        """Test adding book with empty title"""
        success, message = add_book_to_catalog("", "Author", "9780316769174", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Title is required.")
    
    def test_add_book_whitespace_title(self):
        """Test adding book with whitespace-only title"""
        success, message = add_book_to_catalog("   ", "Author", "9780316769174", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Title is required.")
    
    def test_add_book_title_too_long(self):
        """Test adding book with title exceeding 200 characters"""
        long_title = "A" * 201
        success, message = add_book_to_catalog(long_title, "Author", "9780316769174", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Title must be less than 200 characters.")
    
    def test_add_book_title_exactly_200_chars(self):
        """Test adding book with title exactly 200 characters (boundary)"""
        title_200 = "A" * 200
        success, message = add_book_to_catalog(title_200, "Author", "9780316769176", 1)
        self.assertTrue(success)
    
    def test_add_book_empty_author(self):
        """Test adding book with empty author"""
        success, message = add_book_to_catalog("Title", "", "9780316769174", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Author is required.")
    
    def test_add_book_whitespace_author(self):
        """Test adding book with whitespace-only author"""
        success, message = add_book_to_catalog("Title", "   ", "9780316769174", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Author is required.")
    
    def test_add_book_author_too_long(self):
        """Test adding book with author exceeding 100 characters"""
        long_author = "B" * 101
        success, message = add_book_to_catalog("Title", long_author, "9780316769174", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Author must be less than 100 characters.")
    
    def test_add_book_author_exactly_100_chars(self):
        """Test adding book with author exactly 100 characters (boundary)"""
        author_100 = "B" * 100
        success, message = add_book_to_catalog("Title", author_100, "9780316769174", 1)
        self.assertTrue(success)
    
    def test_add_book_isbn_too_short(self):
        """Test adding book with ISBN less than 13 digits"""
        success, message = add_book_to_catalog("Title", "Author", "123456789012", 1)
        self.assertFalse(success)
        self.assertEqual(message, "ISBN must be exactly 13 digits.")
    
    def test_add_book_isbn_too_long(self):
        """Test adding book with ISBN more than 13 digits"""
        success, message = add_book_to_catalog("Title", "Author", "12345678901234", 1)
        self.assertFalse(success)
        self.assertEqual(message, "ISBN must be exactly 13 digits.")
    
    def test_add_book_duplicate_isbn(self):
        """Test adding book with duplicate ISBN"""
        add_book_to_catalog("Book 1", "Author 1", "9780316769174", 1)
        success, message = add_book_to_catalog("Book 2", "Author 2", "9780316769174", 1)
        self.assertFalse(success)
        self.assertEqual(message, "A book with this ISBN already exists.")
    
    def test_add_book_zero_copies(self):
        """Test adding book with zero copies"""
        success, message = add_book_to_catalog("Title", "Author", "9780316769174", 0)
        self.assertFalse(success)
        self.assertEqual(message, "Total copies must be a positive integer.")
    
    def test_add_book_negative_copies(self):
        """Test adding book with negative copies"""
        success, message = add_book_to_catalog("Title", "Author", "9780316769174", -1)
        self.assertFalse(success)
        self.assertEqual(message, "Total copies must be a positive integer.")
    
    def test_add_book_multiple_copies(self):
        """Test adding book with multiple copies"""
        success, message = add_book_to_catalog("Title", "Author", "9780316769177", 10)
        self.assertTrue(success)
        self.assertIn("successfully added", message)


class TestR3_BorrowBook(TestLibraryService):
    """Test R3: Borrowing Process - borrow_book_by_patron"""
    
    def setUp(self):
        """Set up test data for borrowing tests"""
        super().setUp()
        # Add a test book with unique ISBN
        add_book_to_catalog("Test Book", "Test Author", "9780316769178", 2)
    
    def test_borrow_valid_book(self):
        """Test borrowing a valid available book"""
        success, message = borrow_book_by_patron("123456", 1)
        self.assertTrue(success)
        self.assertIn("Successfully borrowed", message)
        self.assertIn("Due date:", message)
    
    def test_borrow_invalid_patron_id_too_short(self):
        """Test borrowing with patron ID less than 6 digits"""
        success, message = borrow_book_by_patron("12345", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Invalid patron ID. Must be exactly 6 digits.")
    
    def test_borrow_invalid_patron_id_too_long(self):
        """Test borrowing with patron ID more than 6 digits"""
        success, message = borrow_book_by_patron("1234567", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Invalid patron ID. Must be exactly 6 digits.")
    
    def test_borrow_invalid_patron_id_non_numeric(self):
        """Test borrowing with non-numeric patron ID"""
        success, message = borrow_book_by_patron("12345A", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Invalid patron ID. Must be exactly 6 digits.")
    
    def test_borrow_nonexistent_book(self):
        """Test borrowing a book that doesn't exist"""
        success, message = borrow_book_by_patron("123456", 999)
        self.assertFalse(success)
        self.assertEqual(message, "Book not found.")
    
    def test_borrow_unavailable_book(self):
        """Test borrowing a book with no available copies"""
        # Borrow all copies
        borrow_book_by_patron("123456", 1)
        borrow_book_by_patron("234567", 1)
        
        # Try to borrow when none available
        success, message = borrow_book_by_patron("345678", 1)
        self.assertFalse(success)
        self.assertEqual(message, "This book is currently not available.")
    
    def test_borrow_at_limit(self):
        """Test borrowing when patron has exactly 5 books (at limit)"""
        # Add 5 more books (books 2-6)
        for i in range(2, 7):
            add_book_to_catalog(f"Book {i}", "Author", f"978031676918{i}", 1)
        
        # Verify all 6 books exist (book 1 from setUp + books 2-6)
        from database import get_all_books
        all_books = get_all_books()
        self.assertEqual(len(all_books), 6)
        
        # Borrow 5 books (books 1-5)
        for i in range(1, 6):
            success, message = borrow_book_by_patron("123456", i)
            self.assertTrue(success, f"Failed to borrow book {i}: {message}")
        
        # Verify patron has 5 books borrowed
        report = get_patron_status_report("123456")
        self.assertEqual(report['total_books_borrowed'], 5)
        
        # Try to borrow 6th book (should fail at limit)
        success, message = borrow_book_by_patron("123456", 6)
        self.assertFalse(success)
        self.assertEqual(message, "You have reached the maximum borrowing limit of 5 books.")
    
    def test_borrow_due_date_14_days(self):
        """Test that due date is set to 14 days from borrow date"""
        success, message = borrow_book_by_patron("123456", 1)
        self.assertTrue(success)
        
        # Extract due date from message
        expected_due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        self.assertIn(expected_due, message)


class TestR4_ReturnBook(TestLibraryService):
    """Test R4: Return Process - return_book_by_patron"""
    
    def setUp(self):
        """Set up test data for return tests"""
        super().setUp()
        add_book_to_catalog("Test Book", "Test Author", "9780316769179", 2)
        borrow_book_by_patron("123456", 1)
    
    def test_return_valid_book(self):
        """Test returning a borrowed book"""
        success, message = return_book_by_patron("123456", 1)
        self.assertTrue(success)
        self.assertIn("Successfully returned", message)
    
    def test_return_invalid_patron_id(self):
        """Test returning with invalid patron ID"""
        success, message = return_book_by_patron("12345", 1)
        self.assertFalse(success)
        self.assertEqual(message, "Invalid patron ID. Must be exactly 6 digits.")
    
    def test_return_nonexistent_book(self):
        """Test returning a book that doesn't exist"""
        success, message = return_book_by_patron("123456", 999)
        self.assertFalse(success)
        self.assertEqual(message, "Book not found.")
    
    def test_return_not_borrowed_book(self):
        """Test returning a book the patron doesn't have borrowed"""
        success, message = return_book_by_patron("234567", 1)
        self.assertFalse(success)
        self.assertEqual(message, "You do not have this book borrowed.")
    
    def test_return_increases_availability(self):
        """Test that returning a book increases available copies"""
        from database import get_book_by_id
        
        # Check availability before return
        book_before = get_book_by_id(1)
        available_before = book_before['available_copies']
        
        # Return book
        return_book_by_patron("123456", 1)
        
        # Check availability after return
        book_after = get_book_by_id(1)
        available_after = book_after['available_copies']
        
        self.assertEqual(available_after, available_before + 1)
    
    def test_return_already_returned_book(self):
        """Test returning a book that was already returned"""
        return_book_by_patron("123456", 1)
        success, message = return_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertEqual(message, "You do not have this book borrowed.")


class TestR5_LateFeeCalculation(TestLibraryService):
    """Test R5: Late Fee Calculation - calculate_late_fee_for_book"""
    
    def setUp(self):
        """Set up test data for late fee tests"""
        super().setUp()
        add_book_to_catalog("Test Book", "Test Author", "9780316769180", 1)
    
    def test_calculate_fee_invalid_patron_id(self):
        """Test fee calculation with invalid patron ID"""
        result = calculate_late_fee_for_book("12345", 1)
        self.assertEqual(result['fee_amount'], 0.00)
        self.assertEqual(result['days_overdue'], 0)
        self.assertEqual(result['status'], "Invalid patron ID")
    
    def test_calculate_fee_not_borrowed(self):
        """Test fee calculation for book not borrowed by patron"""
        result = calculate_late_fee_for_book("123456", 1)
        self.assertEqual(result['fee_amount'], 0.00)
        self.assertEqual(result['days_overdue'], 0)
        self.assertEqual(result['status'], "Book not currently borrowed by this patron")
    
    def test_calculate_fee_not_overdue(self):
        """Test fee calculation for book not yet overdue"""
        borrow_book_by_patron("123456", 1)
        result = calculate_late_fee_for_book("123456", 1)
        self.assertEqual(result['fee_amount'], 0.00)
        self.assertEqual(result['days_overdue'], 0)
        self.assertEqual(result['status'], "Book is not overdue")
    
    def test_calculate_fee_overdue_book(self):
        """Test fee calculation for overdue book (manual database modification)"""
        from database import get_db_connection
        
        # Borrow book
        borrow_book_by_patron("123456", 1)
        
        # Manually set due date to 5 days ago
        conn = get_db_connection()
        past_due = (datetime.now() - timedelta(days=5)).isoformat()
        conn.execute(
            "UPDATE borrow_records SET due_date = ? WHERE patron_id = ? AND book_id = ?",
            (past_due, "123456", 1)
        )
        conn.commit()
        conn.close()
        
        # Calculate fee
        result = calculate_late_fee_for_book("123456", 1)
        self.assertEqual(result['days_overdue'], 5)
        self.assertEqual(result['fee_amount'], 2.50)  # 5 days * $0.50
        self.assertIn("Overdue by 5 day(s)", result['status'])
    
    def test_calculate_fee_rate_50_cents_per_day(self):
        """Test that fee rate is $0.50 per day for first 7 days"""
        from database import get_db_connection
        
        borrow_book_by_patron("123456", 1)
        
        # Set due date to 5 days ago (within first 7 days)
        conn = get_db_connection()
        past_due = (datetime.now() - timedelta(days=5)).isoformat()
        conn.execute(
            "UPDATE borrow_records SET due_date = ? WHERE patron_id = ? AND book_id = ?",
            (past_due, "123456", 1)
        )
        conn.commit()
        conn.close()
        
        result = calculate_late_fee_for_book("123456", 1)
        self.assertEqual(result['days_overdue'], 5)
        self.assertEqual(result['fee_amount'], 2.50)  # 5 * $0.50
    
    def test_calculate_fee_tiered_after_7_days(self):
        """Test that fee rate changes to $1.00/day after 7 days"""
        from database import get_db_connection
        
        borrow_book_by_patron("123456", 1)
        
        # Set due date to 10 days ago (3 days past the 7-day threshold)
        conn = get_db_connection()
        past_due = (datetime.now() - timedelta(days=10)).isoformat()
        conn.execute(
            "UPDATE borrow_records SET due_date = ? WHERE patron_id = ? AND book_id = ?",
            (past_due, "123456", 1)
        )
        conn.commit()
        conn.close()
        
        result = calculate_late_fee_for_book("123456", 1)
        self.assertEqual(result['days_overdue'], 10)
        # 7 * $0.50 + 3 * $1.00 = $3.50 + $3.00 = $6.50
        self.assertEqual(result['fee_amount'], 6.50)
    
    def test_calculate_fee_maximum_cap_15_dollars(self):
        """Test that late fees are capped at $15.00 maximum"""
        from database import get_db_connection
        
        borrow_book_by_patron("123456", 1)
        
        # Set due date to 30 days ago (would exceed $15 cap)
        conn = get_db_connection()
        past_due = (datetime.now() - timedelta(days=30)).isoformat()
        conn.execute(
            "UPDATE borrow_records SET due_date = ? WHERE patron_id = ? AND book_id = ?",
            (past_due, "123456", 1)
        )
        conn.commit()
        conn.close()
        
        result = calculate_late_fee_for_book("123456", 1)
        self.assertEqual(result['days_overdue'], 30)
        # Without cap: 7 * $0.50 + 23 * $1.00 = $26.50
        # With cap: $15.00
        self.assertEqual(result['fee_amount'], 15.00)


class TestR6_SearchBooks(TestLibraryService):
    """Test R6: Book Search - search_books_in_catalog"""
    
    def setUp(self):
        """Set up test data for search tests"""
        super().setUp()
        add_book_to_catalog("The Great Gatsby", "F. Scott Fitzgerald", "9780743273560", 3)
        add_book_to_catalog("The Catcher in the Rye", "J.D. Salinger", "9780316769181", 2)
        add_book_to_catalog("To Kill a Mockingbird", "Harper Lee", "9780061120080", 1)
    
    def test_search_by_title_exact_match(self):
        """Test searching by exact title match"""
        results = search_books_in_catalog("The Great Gatsby", "title")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "The Great Gatsby")
    
    def test_search_by_title_partial_match(self):
        """Test searching by partial title match"""
        results = search_books_in_catalog("Great", "title")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "The Great Gatsby")
    
    def test_search_by_title_case_insensitive(self):
        """Test that title search is case-insensitive"""
        results = search_books_in_catalog("great gatsby", "title")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "The Great Gatsby")
    
    def test_search_by_title_multiple_results(self):
        """Test searching by title returning multiple results"""
        results = search_books_in_catalog("The", "title")
        # Only 2 books contain "The" in the title: "The Great Gatsby" and "The Catcher in the Rye"
        # "To Kill a Mockingbird" does not contain "The"
        self.assertEqual(len(results), 2)
    
    def test_search_by_author_exact_match(self):
        """Test searching by exact author match"""
        results = search_books_in_catalog("Harper Lee", "author")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['author'], "Harper Lee")
    
    def test_search_by_author_partial_match(self):
        """Test searching by partial author match"""
        results = search_books_in_catalog("Fitzgerald", "author")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['author'], "F. Scott Fitzgerald")
    
    def test_search_by_author_case_insensitive(self):
        """Test that author search is case-insensitive"""
        results = search_books_in_catalog("harper lee", "author")
        self.assertEqual(len(results), 1)
    
    def test_search_by_isbn_exact_match(self):
        """Test searching by ISBN (exact match only)"""
        results = search_books_in_catalog("9780743273560", "isbn")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['isbn'], "9780743273560")
    
    def test_search_by_isbn_no_partial_match(self):
        """Test that ISBN search doesn't match partial ISBNs"""
        results = search_books_in_catalog("978074327", "isbn")
        self.assertEqual(len(results), 0)
    
    def test_search_empty_term(self):
        """Test searching with empty search term"""
        results = search_books_in_catalog("", "title")
        self.assertEqual(len(results), 0)
    
    def test_search_whitespace_term(self):
        """Test searching with whitespace-only search term"""
        results = search_books_in_catalog("   ", "title")
        self.assertEqual(len(results), 0)
    
    def test_search_invalid_type(self):
        """Test searching with invalid search type"""
        results = search_books_in_catalog("Test", "invalid_type")
        self.assertEqual(len(results), 0)
    
    def test_search_no_results(self):
        """Test searching with term that matches nothing"""
        results = search_books_in_catalog("Nonexistent Book", "title")
        self.assertEqual(len(results), 0)


class TestR7_PatronStatusReport(TestLibraryService):
    """Test R7: Patron Status Report - get_patron_status_report"""
    
    def setUp(self):
        """Set up test data for patron status tests"""
        super().setUp()
        add_book_to_catalog("Book 1", "Author 1", "9780743273561", 1)
        add_book_to_catalog("Book 2", "Author 2", "9780316769182", 1)
        add_book_to_catalog("Book 3", "Author 3", "9780061120081", 1)
    
    def test_status_invalid_patron_id(self):
        """Test status report with invalid patron ID"""
        report = get_patron_status_report("12345")
        self.assertEqual(report['status'], "Invalid patron ID")
        self.assertEqual(report['total_books_borrowed'], 0)
    
    def test_status_no_books_borrowed(self):
        """Test status report for patron with no borrowed books"""
        report = get_patron_status_report("123456")
        self.assertEqual(report['patron_id'], "123456")
        self.assertEqual(report['total_books_borrowed'], 0)
        self.assertEqual(report['total_late_fees'], 0.00)
        self.assertEqual(report['status'], "No books currently borrowed")
    
    def test_status_with_borrowed_books(self):
        """Test status report for patron with borrowed books"""
        borrow_book_by_patron("123456", 1)
        borrow_book_by_patron("123456", 2)
        
        report = get_patron_status_report("123456")
        self.assertEqual(report['patron_id'], "123456")
        self.assertEqual(report['total_books_borrowed'], 2)
        self.assertEqual(len(report['borrowed_books']), 2)
        self.assertEqual(report['status'], "Active")
    
    def test_status_with_overdue_books(self):
        """Test status report with overdue books and fees"""
        from database import get_db_connection
        
        # Borrow books
        borrow_book_by_patron("123456", 1)
        borrow_book_by_patron("123456", 2)
        
        # Make first book overdue by 5 days
        conn = get_db_connection()
        past_due = (datetime.now() - timedelta(days=5)).isoformat()
        conn.execute(
            "UPDATE borrow_records SET due_date = ? WHERE patron_id = ? AND book_id = ?",
            (past_due, "123456", 1)
        )
        conn.commit()
        conn.close()
        
        report = get_patron_status_report("123456")
        self.assertEqual(report['total_books_borrowed'], 2)
        self.assertEqual(report['total_late_fees'], 2.50)  # 5 days * $0.50
        
        # Check first book is marked overdue
        book1 = [b for b in report['borrowed_books'] if b['book_id'] == 1][0]
        self.assertTrue(book1['is_overdue'])
        self.assertEqual(book1['days_overdue'], 5)
        self.assertEqual(book1['late_fee'], 2.50)
        
        # Check second book is not overdue
        book2 = [b for b in report['borrowed_books'] if b['book_id'] == 2][0]
        self.assertFalse(book2['is_overdue'])
        self.assertEqual(book2['days_overdue'], 0)
        self.assertEqual(book2['late_fee'], 0.00)
    
    def test_status_report_contains_all_fields(self):
        """Test that status report contains all required fields"""
        borrow_book_by_patron("123456", 1)
        report = get_patron_status_report("123456")
        
        # Check report structure
        self.assertIn('patron_id', report)
        self.assertIn('borrowed_books', report)
        self.assertIn('total_books_borrowed', report)
        self.assertIn('total_late_fees', report)
        self.assertIn('status', report)
        
        # Check borrowed book structure
        book = report['borrowed_books'][0]
        self.assertIn('book_id', book)
        self.assertIn('title', book)
        self.assertIn('author', book)
        self.assertIn('borrow_date', book)
        self.assertIn('due_date', book)
        self.assertIn('is_overdue', book)
        self.assertIn('days_overdue', book)
        self.assertIn('late_fee', book)
    
   



class TestIntegrationScenarios(TestLibraryService):
    """Integration tests for complete workflows"""
    
    def test_complete_borrow_return_workflow(self):
        """Test complete workflow: add book -> borrow -> return"""
        # Add book
        success, _ = add_book_to_catalog("Test Book", "Test Author", "9780743273562", 1)
        self.assertTrue(success)
        
        # Borrow book
        success, _ = borrow_book_by_patron("123456", 1)
        self.assertTrue(success)
        
        # Return book
        success, _ = return_book_by_patron("123456", 1)
        self.assertTrue(success)
        
        # Verify patron has no borrowed books
        report = get_patron_status_report("123456")
        self.assertEqual(report['total_books_borrowed'], 0)
    
    def test_multiple_patrons_same_book(self):
        """Test multiple patrons borrowing copies of the same book"""
        # Add book with 3 copies
        add_book_to_catalog("Popular Book", "Famous Author", "9780743273563", 3)
        
        # Three patrons borrow
        borrow_book_by_patron("123456", 1)
        borrow_book_by_patron("234567", 1)
        borrow_book_by_patron("345678", 1)
        
        # Fourth patron should fail
        success, message = borrow_book_by_patron("456789", 1)
        self.assertFalse(success)
        self.assertEqual(message, "This book is currently not available.")
    
    def test_search_and_borrow_workflow(self):
        """Test searching for a book and then borrowing it"""
        # Add books
        add_book_to_catalog("Python Programming", "John Doe", "9780743273564", 1)
        add_book_to_catalog("Java Programming", "Jane Smith", "9780316769183", 1)
        
        # Search for Python book
        results = search_books_in_catalog("Python", "title")
        self.assertEqual(len(results), 1)
        
        # Borrow the found book
        book_id = results[0]['id']
        success, _ = borrow_book_by_patron("123456", book_id)
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main(verbosity=2)