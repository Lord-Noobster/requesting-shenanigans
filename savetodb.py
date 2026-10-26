import sqlite3
import time
import requests

HEADER = {"User-Agent": "learning_project (jonizan@pm.me)"}
MIN_INTERVAL = (
    1.5  # seconds between API calls openlibrary allows 3/sec with a header with email
)
_last_call = 0.0


def init_db(path="books.db"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            isbn TEXT PRIMARY KEY,
            title TEXT,
            author TEXT,
            publisher TEXT,
            publish_date DATE,
            pages INTEGER,
            status TEXT DEFAULT 'owned',
            rating INTEGER,
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def throttle():
    global _last_call
    wait = MIN_INTERVAL - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()


def fetch_isbn(title, limit=1, max_isbns=5):
    throttle()
    try:
        response_title = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "fields": "isbn",
                "limit": limit,
            },
            headers=HEADER,
            timeout=10,
        )
        response_title.raise_for_status()
        docs = response_title.json().get("docs")
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return []
    if not docs:
        return []
    return (docs[0].get("isbn") or [])[:max_isbns]


def fetch_from_api(isbn):
    throttle()
    book = None
    try:
        r = requests.get(
            "https://openlibrary.org/api/books",
            params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
            headers=HEADER,
            timeout=10,
        )
        r.raise_for_status()
        book = r.json().get(f"ISBN:{isbn}")
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
    if not book:
        return
    authors = book.get("authors") or [{}]
    publishers = book.get("publishers") or [{}]

    return {
        "isbn": isbn,
        "title": book.get("title"),
        "author": authors[0].get("name"),
        "publisher": publishers[0].get("name"),
        "publish_date": book.get("publish_date"),
        "pages": book.get("number_of_pages"),
    }


def get_book(conn, title):
    row = conn.execute(
        "SELECT * FROM books WHERE title = ?", (f"%{title}%",)
    ).fetchone()
    if row:
        return dict(row)
    for isbn in fetch_isbn(title):
        data = fetch_from_api(isbn)
        if data:
            with conn:
                conn.execute(
                    "INSERT OR IGNORE INTO books (isbn, title, author, publisher, publish_date, pages)"
                    "VALUES (:isbn, :title, :author, :publisher, :publish_date, :pages )",
                    data,
                )
                return data
    return None


def menu():
    conn = init_db()
    book_query = input("which book are we looking for?: ")
    print(get_book(conn, book_query) or "no result")
    conn.close()


menu()
