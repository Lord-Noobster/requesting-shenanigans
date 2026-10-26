import requests
import json


def lookup(isbn):
    book = None
    try:
        r = requests.get(
            "https://openlibrary.org/api/books",
            params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
            headers={"User-Agent": "learning_project (jonizan@pm.me)"},
            timeout=10,
        )

        r.raise_for_status()
        book = r.json().get(f"ISBN:{isbn}")

    except requests.exceptions.Timeout:
        print("Timed out")
    except requests.exceptions.ConnectionError:
        print("Could not connect")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        print(f"Rejected: {status}")
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")

    if not book:
        return None
        # open library queries works not singular editions to avoid a list
        # multiple editions i just choose the first from the list of authors and publishers
    authors = book.get("authors") or [{}]
    publishers = book.get("publishers") or [{}]

    return {
        "isbn": isbn,
        "title": book.get("title"),
        "author": authors[0].get("name"),
        "publisher": publishers[0].get("name"),
        "publish_date": book.get("publish_date"),
        "by_statement": book.get("by_statement"),
        "notes": book.get("notes"),
    }


def query():
    print("this is a basic book metadata fetcher\n\n\n")

    user_input = input("please enter the ISBN of your query: ")

    result = lookup(user_input)

    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))

        with open(f"{user_input}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print("no result xyz")


query()
