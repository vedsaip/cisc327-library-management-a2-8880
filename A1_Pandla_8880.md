# CISC327 – Assignment 1

**Name:** Vedsai Pandla  
**Student ID:** 20348880

---

## Implementation Status Report

### R1 – Add books

**Status:** Complete with bugs
**Findings:** The add_book_to_catalog() function is fully implemented and meets all requirements. It properly validates title (max 200 chars), author (max 100 chars), ISBN (exactly 13 digits), and total copies (positive integer). The function prevents duplicate ISBN entries and provides appropriate success/error messages with proper database error handling.

---

### R2 – Patron Account Management

**Status:** Complete with bugs
**Findings:** No implementation exists for the catalog display functionality. The system lacks functions to retrieve and format the book list for web display. Missing components include pagination for large catalogs, sorting capabilities by title/author/availability, and proper formatting for the web interface template system.

---

### R3 – Book Borrowing Interface

**Status:** Complete with bugs
**Findings:** The function works for borrowing books but has three intentional issues:

- Borrow limit uses > 5 instead of >= 5, allowing 6 books.
- Message wording is "Successfully borrowed..." instead of "borrowed successfully...", causing test mismatch.
- Patron ID validation requires exactly 6 digits, while sample tests use IDs like "patron1".

---

### R4 - Return Books

**Status:** Partial/Incomplete
**Findings:** The function verifies that the book was borrowed and updates availability. However:

- Late fee calculation is not integrated into the return process.
- No explicit user-facing message about fees is provided.
- Function is not implemented in library_service.py so it is not feasible to test properly

---

### R5 – Late Fee calculation

**Status:** Incomplete  
**Findings:** The fee calculation logic matches requirements:

- 14-day due date
- $0.50/day for first 7 days, $1.00/day afterward
- Maximum fee capped at $15.00  
  **Missing:** API endpoint /api/late_fee/<patron_id>/<book_id> and the rest of the function are not implemented, which makes properly testing not possible.

---

### R6 – Search Functionality

**Status:** Incomplete  
**Findings:** The search_books wrapper exists, but:

- Title and author searches are likely case-sensitive, not case-insensitive as required.
- ISBN may not enforce exact matching, depending on database query.  
  -This function also does not exist in library_service.py so testing properly is not possible.

---

### R7 – Patron Status Report

**Status:** Incomplete
**Findings:** No dedicated function for generating a patron’s status report exists in library_service.py.

---
