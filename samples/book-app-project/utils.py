def print_menu():
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")


def get_user_choice() -> str:
    while True:
        choice = input("Choose an option (1-5): ").strip()
        
        if not choice:
            print("Error: Please enter a value.")
            continue
        
        if not choice.isdigit():
            print("Error: Please enter a number.")
            continue
        
        if choice not in ['1', '2', '3', '4', '5']:
            print("Error: Please enter a number between 1 and 5.")
            continue
        
        return choice


def get_book_details():
    """
    Collect book information from the user through interactive prompts.
    
    This function prompts the user to enter a book's title, author, and publication
    year. It validates that title and author are not empty, re-prompting if necessary.
    The year is optional and defaults to 0 if invalid input is provided.
    
    Returns:
        tuple: A tuple containing three elements:
            - title (str): The book's title (guaranteed to be non-empty)
            - author (str): The book's author (guaranteed to be non-empty)
            - year (int): The publication year (defaults to 0 if invalid)
    
    Examples:
        >>> title, author, year = get_book_details()
        Enter book title: The Great Gatsby
        Enter author: F. Scott Fitzgerald
        Enter publication year: 1925
        >>> print(title, author, year)
        The Great Gatsby F. Scott Fitzgerald 1925
    """
    while True:
        title = input("Enter book title: ").strip()
        if title:
            break
        print("Error: Title cannot be empty.")
    
    while True:
        author = input("Enter author: ").strip()
        if author:
            break
        print("Error: Author cannot be empty.")

    year_input = input("Enter publication year: ").strip()
    try:
        year = int(year_input)
    except ValueError:
        print("Invalid year. Defaulting to 0.")
        year = 0

    return title, author, year


def print_books(books):
    if not books:
        print("No books in your collection.")
        return

    print("\nYour Books:")
    for index, book in enumerate(books, start=1):
        status = "✅ Read" if book.read else "📖 Unread"
        print(f"{index}. {book.title} by {book.author} ({book.year}) - {status}")
