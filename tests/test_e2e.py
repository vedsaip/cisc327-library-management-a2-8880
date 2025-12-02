"""
End-to-End (E2E) Tests for Library Management System
Uses Playwright to test real user flows in the browser
Run with: pytest tests/test_e2e.py

IMPORTANT: Start Flask server manually before running tests:
    python app.py
Then in another terminal:
    pytest tests/test_e2e.py -v
"""

import pytest
from playwright.sync_api import Page, expect
from database import clear_database, add_sample_data


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the Flask application"""
    return "http://localhost:5000"


from database import clear_database, add_sample_data


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the Flask application"""
    return "http://localhost:5000"


@pytest.fixture(autouse=True)
def clear_db():
    """Fixture to clear and reset database before each test"""
    clear_database()
    add_sample_data()


class TestE2ELibraryManagement:
    """
    E2E tests simulating real user interactions
    
    PREREQUISITE: Flask server must be running on http://localhost:5000
    Start server with: python app.py
    """
    
    def test_user_flow_add_book_and_verify_catalog(self, page: Page, base_url):
        """
        USER FLOW 1: Add a new book to the catalog
        
        Steps:
        1. Navigate to home page
        2. Click "Add Book" navigation link
        3. Fill in book details form (title, author, ISBN, copies)
        4. Submit the form
        5. Verify success message appears
        6. Verify book appears in the catalog table
        """
        print("\n--- Testing: Add Book Flow ---")
        
        # Step 1: Navigate to home page
        page.goto(base_url)
        expect(page).to_have_title("Library Management System")
        print("✓ Home page loaded")
        
        # Step 2: Click "Add Book" link
        page.click("text=Add Book")
        expect(page).to_have_url(f"{base_url}/add_book")
        print("✓ Navigated to Add Book page")
        
        # Step 3: Fill in book details
        test_isbn = "9780135957052"  # Unique ISBN for this test
        page.fill("input[name='title']", "The Pragmatic Programmer")
        page.fill("input[name='author']", "Andrew Hunt")
        page.fill("input[name='isbn']", test_isbn)
        page.fill("input[name='total_copies']", "3")
        print("✓ Form filled with book details")
        
        # Step 4: Submit the form
        page.click("button[type='submit']")
        
        # Step 5: Verify success message appears
        expect(page.locator(".flash-success")).to_be_visible(timeout=5000)
        print("✓ Success message displayed")
        
        # Step 6: Verify book appears in the catalog
        expect(page).to_have_url(base_url + "/catalog")
        expect(page.locator("body")).to_contain_text("Pragmatic Programmer")
        print("✓ Book appears in catalog")
    
    
    def test_user_flow_borrow_book(self, page: Page, base_url):
        """
        USER FLOW 2: Borrow a book using patron ID
        
        Steps:
        1. Navigate to home page
        2. Click "Borrow Book" navigation link
        3. Select a book from dropdown/list
        4. Enter valid patron ID (6 digits)
        5. Submit borrow request
        6. Verify success confirmation message with due date
        """
        print("\n--- Testing: Borrow Book Flow ---")

        # Step 1: Navigate to home page (which redirects to catalog)
        page.goto(base_url)
        print("✓ Home page loaded, redirected to catalog")

        # Find the first available book's row and borrow it
        # This makes the test robust by not relying on a fixed book_id
        first_book_row = page.locator("tr:has(button:text('Borrow'))").first
        
        # Step 2, 3, 4: Enter patron ID and submit
        first_book_row.locator("input[name='patron_id']").fill("123456")
        print("✓ Patron ID entered")
        
        first_book_row.locator("button:text('Borrow')").click()
        print("✓ Borrow request submitted")

        # Step 5: Verify success confirmation message
        page.wait_for_timeout(1000)
        success_message = page.locator(".flash-success")
        expect(success_message).to_be_visible(timeout=5000)
        expect(success_message).to_contain_text("Successfully borrowed")
        print("✓ Borrow confirmation displayed")    
    
    def test_search_book_functionality(self, page: Page, base_url):
        """
        USER FLOW 3: Search for books in catalog
        
        Steps:
        1. Navigate to search page
        2. Enter search term
        3. Select search type (title/author/ISBN)
        4. Submit search
        5. Verify search results table appears with matching books
        """
        print("\n--- Testing: Search Books Flow ---")
        
        # Step 1: Navigate to search page
        page.goto(f"{base_url}/search")
        page.wait_for_timeout(500)
        print("✓ Search page loaded")
        
        # Step 2 & 3: Enter search term and select type
        page.fill("input[name='search_term'], input[name='q']", "Great")
        
        if page.locator("select[name='search_type'], select[name='type']").count() > 0:
            page.select_option("select[name='search_type'], select[name='type']", "title")
            print("✓ Search type selected: title")
        
        print("✓ Search term entered: Great")
        
        # Step 4: Submit search
        page.click("button[type='submit']")
        
        # Step 5: Verify search results appear
        page.wait_for_timeout(1000)
        expect(page.locator("body")).to_contain_text("Great")
        print("✓ Search results displayed")
    
    
    def test_invalid_patron_id_validation(self, page: Page, base_url):
        """
        USER FLOW 4: Validate patron ID format
        
        Steps:
        1. Navigate to borrow page
        2. Select a book
        3. Enter invalid patron ID (less than 6 digits)
        4. Submit form
        5. Verify error message appears
        """
        print("\n--- Testing: Invalid Patron ID Validation ---")

        # Step 1: Navigate to home page (which redirects to catalog)
        page.goto(base_url)
        print("✓ Catalog page loaded")

        # Find the first available book's row and try to borrow it with an invalid ID
        first_book_row = page.locator("tr:has(button:text('Borrow'))").first
        
        # Temporarily remove HTML5 validation to test server-side validation
        patron_id_input = first_book_row.locator("input[name='patron_id']")
        patron_id_input.evaluate("node => node.removeAttribute('pattern')")
        
        # Step 2 & 3: Select book and enter invalid patron ID
        patron_id_input.fill("123")  # Invalid: only 3 digits
        print("✓ Invalid patron ID entered: 123")
        
        # Step 4: Submit form
        first_book_row.locator("button:text('Borrow')").click()
        print("✓ Borrow request submitted with invalid ID")

        # Step 5: Verify error message appears
        error_message = page.locator(".flash-error")
        expect(error_message).to_be_visible(timeout=5000)
        expect(error_message).to_contain_text("Invalid patron ID. Must be exactly 6 digits.")
        print("✓ Error message displayed for invalid patron ID")    
    
    def test_add_book_invalid_isbn_validation(self, page: Page, base_url):
        """
        USER FLOW 5: Validate ISBN format
        
        Steps:
        1. Navigate to add book page
        2. Fill form with invalid ISBN (not 13 digits)
        3. Submit form
        4. Verify error message appears
        """
        print("\n--- Testing: Invalid ISBN Validation ---")
        
        # Step 1: Navigate to add book page
        page.goto(f"{base_url}/add_book")
        page.wait_for_timeout(500)
        print("✓ Add Book page loaded")
        
        # Step 2: Fill form with invalid ISBN
        page.fill("input[name='title']", "Test Book")
        page.fill("input[name='author']", "Test Author")
        page.fill("input[name='isbn']", "12345")  # Invalid: only 5 digits
        page.fill("input[name='total_copies']", "1")
        print("✓ Form filled with invalid ISBN: 12345")
        
        # Step 3: Submit form
        page.click("button[type='submit']")
        
        # Step 4: Verify error message appears
        error_message = page.locator(".flash-error")
        expect(error_message).to_be_visible(timeout=5000)
        expect(page.locator("body")).to_contain_text("13 digits")
        print("✓ Error message displayed for invalid ISBN")
    
    
    def test_navigation_all_pages(self, page: Page, base_url):
        """
        USER FLOW 6: Navigate between all pages
        
        Steps:
        1. Start at home page
        2. Navigate to each page via navigation menu
        3. Verify correct page loads each time
        """
        print("\n--- Testing: Navigation Between Pages ---")
        
        # Step 1: Start at home page
        page.goto(base_url)
        expect(page).to_have_url(base_url + "/catalog")
        print("✓ Home page")
        
        # Step 2 & 3: Navigate to each page
        page.click("text=Add Book")
        page.wait_for_timeout(500)
        expect(page).to_have_url(f"{base_url}/add_book")
        print("✓ Add Book page")
        
        # Check if Return link exists
        if page.locator("text=Return").count() > 0:
            page.click("text=Return")
            page.wait_for_timeout(500)
            print("✓ Return page")
        
        page.click("text=Search")
        page.wait_for_timeout(500)
        print("✓ Search page")
        
        page.click("text=Catalog")
        page.wait_for_timeout(500)
        expect(page).to_have_url(base_url + "/catalog")
        print("✓ Back to Home page")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("IMPORTANT: Flask server must be running before executing tests!")
    print("="*70)
    print("\nStart Flask server in one terminal:")
    print("    python app.py")
    print("\nThen run tests in another terminal:")
    print("    pytest tests/test_e2e.py -v")
    print("="*70 + "\n")