import requests

HEADER = {"User-Agen": "learning_project (jonizan@pm.me)"}


def search_title(title, limit=3):
    try:
        r = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "fields": "title,author_name,first_publish_year,isbn",
                "limit": limit,
            },
            headers=HEADER,
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("docs") or []
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return []


def query():
    title = input("book title: ")
    docs = search_title(title)
    if not docs:
        print("no result")
        return

    for i, d in enumerate(docs, 1):
        author = (d.get("author_name") or ["?"])[0]
        year = d.get("first_publish_year", "?")
        isbns = d.get("isbn") or []
        isbn13 = next((x for x in isbns if len(x) == 13), None)
        print(
            f"{i}. {d.get('title')} - {author} ({year}) ISBN: {isbn13 or isbns[:1] or 'none'}"
        )


query()
