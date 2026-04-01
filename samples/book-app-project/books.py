import json
import os
import tempfile
import unicodedata
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple

DATA_FILE = "data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    def __init__(self):
        self.books: List[Book] = []
        self.load_books()

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print(f"Warning: {DATA_FILE} is corrupted. Starting with empty collection.")
            self.books = []
        except OSError as e:
            # Covers PermissionError, IsADirectoryError, etc.
            print(f"Warning: Cannot read {DATA_FILE}: {e}. Starting with empty collection.")
            self.books = []

    def save_books(self):
        """Save the current book collection to JSON using an atomic write.

        Writes to a temporary file and then atomically replaces the data file. If
        writing or replacing fails an OSError is raised so callers can handle
        persistence failures and avoid silently losing in-memory state.
        """
        try:
            dir_name = os.path.dirname(os.path.abspath(DATA_FILE)) or "."
            os.makedirs(dir_name, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=os.path.basename(DATA_FILE), text=True)
            with os.fdopen(fd, "w") as f:
                json.dump([asdict(b) for b in self.books], f, indent=2)
            os.replace(tmp_path, DATA_FILE)
        except (OSError, IOError) as e:
            raise OSError(f"Failed to save books: {e}") from e

    def add_book(self, title: str, author: str, year: int) -> Book:
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        try:
            self.save_books()
        except Exception:
            # Roll back on failure to persist
            try:
                self.books.remove(book)
            except ValueError:
                pass
            raise
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: Optional[str]) -> Optional[Book]:
        """Find a book by exact title (case- and unicode-normalized).

        Returns None if title is None or no match is found.
        """
        if title is None:
            return None
        target = unicodedata.normalize("NFKC", title.strip()).casefold()
        for book in self.books:
            try:
                btitle = unicodedata.normalize("NFKC", book.title.strip()).casefold()
            except Exception:
                # Skip malformed entries
                continue
            if btitle == target:
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        book = self.find_book_by_title(title)
        if book:
            prev = book.read
            book.read = True
            try:
                self.save_books()
            except Exception:
                # Restore previous state on failure
                book.read = prev
                raise
            return True
        return False

    def remove_book(self, title: str) -> Tuple[bool, str]:
        """Remove a book by title and return (success, message).

        The function performs a case- and unicode-normalized exact match first.
        If no exact match is found it searches for partial (substring) matches to
        suggest possible titles. On persistence failure the in-memory change is
        rolled back and the underlying exception is propagated.
        """
        if not title or not title.strip():
            return False, "No title provided."

        book = self.find_book_by_title(title)
        if not book:
            # Suggest partial matches to help the user
            target = unicodedata.normalize("NFKC", title.strip()).casefold()
            candidates = []
            for b in self.books:
                try:
                    btitle = unicodedata.normalize("NFKC", b.title.strip()).casefold()
                except Exception:
                    continue
                if target in btitle:
                    candidates.append(b.title)

            if candidates:
                suggestion = ", ".join(candidates)
                return False, f"No exact match for '{title}'. Did you mean: {suggestion}?"
            return False, f"No book found with title '{title}'."

        # Found exact match: remove and persist with rollback on failure
        # Preserve the original index so rollback restores order
        original_index = None
        for i, b in enumerate(self.books):
            if b is book:
                original_index = i
                break

        if original_index is not None:
            # Remove by index to avoid ambiguity
            self.books.pop(original_index)
        else:
            # Fallback
            self.books.remove(book)

        try:
            self.save_books()
        except Exception:
            # Roll back the removal on failure to persist
            if original_index is not None:
                self.books.insert(original_index, book)
            else:
                self.books.append(book)
            raise

        return True, f"Removed '{book.title}' by {book.author}."

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author using unicode-normalized case-insensitive match.

        Returns an empty list if `author` is falsy.
        """
        if not author:
            return []
        target = unicodedata.normalize("NFKC", author.strip()).casefold()
        results = []
        for b in self.books:
            try:
                bauthor = unicodedata.normalize("NFKC", b.author.strip()).casefold()
            except Exception:
                continue
            if bauthor == target:
                results.append(b)
        return results
