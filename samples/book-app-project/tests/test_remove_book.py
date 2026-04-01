import json
import os
import sys
import pytest

# Ensure the package modules in the parent dir are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from books import BookCollection


def make_collection(tmp_path):
    # Import and reload the books module, then set DATA_FILE before creating the
    # BookCollection instance so it uses the temporary file.
    from importlib import reload
    import books as books_mod

    reload(books_mod)
    books_mod.DATA_FILE = str(tmp_path / "data.json")

    # Ensure file doesn't exist at start
    try:
        os.remove(books_mod.DATA_FILE)
    except OSError:
        pass

    # Instantiate after setting DATA_FILE so load_books uses the temp path
    return books_mod.BookCollection(), books_mod


def read_data_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def test_remove_existing_book(tmp_path):
    collection, books_mod = make_collection(tmp_path)

    # Add a book and persist
    collection.add_book("Dune", "Frank Herbert", 1965)
    assert len(collection.list_books()) == 1

    success, message = collection.remove_book("Dune")
    assert success is True
    assert "Removed 'Dune'" in message
    assert len(collection.list_books()) == 0

    # Ensure data file updated
    data = read_data_file(books_mod.DATA_FILE)
    assert isinstance(data, list)
    assert len(data) == 0


def test_remove_case_insensitive(tmp_path):
    collection, books_mod = make_collection(tmp_path)

    collection.add_book("Dune", "Frank Herbert", 1965)
    # Remove using different case
    success, message = collection.remove_book("dUnE")
    assert success is True
    assert "Removed 'Dune'" in message
    assert len(collection.list_books()) == 0


def test_remove_nonexistent_returns_feedback(tmp_path):
    collection, books_mod = make_collection(tmp_path)

    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    success, message = collection.remove_book("Dune")
    assert success is False
    # Message should either suggest candidates or say no book found
    assert ("No exact match" in message) or ("No book found" in message)
    # Ensure original book still present
    assert len(collection.list_books()) == 1


def test_remove_from_empty_collection(tmp_path):
    collection, books_mod = make_collection(tmp_path)

    assert len(collection.list_books()) == 0
    success, message = collection.remove_book("Dune")
    assert success is False
    assert "No book found" in message or "No exact match" in message
    # Still empty
    assert len(collection.list_books()) == 0
