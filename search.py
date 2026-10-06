import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 Safari/605.1"
    )
}


def extract_terms(request):
    text = request.lower()

    terms = []

    if "баннер" in text or "banner" in text:
        terms += [
            "нужен баннер",
            "нужны баннеры",
            "нужен дизайнер",
            "ищем дизайнера",
            "заказать баннер",
            "дизайн рекламы",
            "рекламный креатив",
        ]

    if "дизайн" in text:
        terms += [
            "нужен дизайнер",
            "ищем дизайнера",
            "заказать дизайн",
            "дизайн рекламы",
        ]

    if "сайт" in text:
        terms += [
            "нужен сайт",
            "нужен веб дизайнер",
            "лендинг",
        ]

    if not terms:
        terms = [
            x for x in re.findall(
                r"[A-Za-zА-Яа-яЁё0-9_-]{4,}",
                text
            )
        ][:8]

    return list(dict.fromkeys(terms))


def search_web(query, limit=30):
    url = (
        "https://www.google.com/search?q="
        + quote(query)
        + "&num="
        + str(limit)
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    results = []

    for item in soup.select("div.MjjYud"):

        link_tag = item.select_one("a")

        if not link_tag:
            continue

        link = link_tag.get("href", "")

        title_tag = item.select_one("h3")

        if not title_tag:
            continue

        title = title_tag.get_text(
            " ",
            strip=True
        )

        text = item.get_text(
            " ",
            strip=True
        )

        if "t.me/" not in link:
            continue

        results.append({
            "name": title,
            "link": link,
            "text": text[:1800]
        })

    return results


async def telegram_search(request, limit=150):

    terms = extract_terms(request)

    print(
        "[SEARCH] Ищу публичные Telegram-источники..."
    )

    found = {}

    for term in terms:

        query = f'site:t.me "{term}"'

        print(
            f"[SEARCH] {term}"
        )

        try:
            results = search_web(
                query,
                limit=30
            )

        except Exception as error:

            print(
                f"[SEARCH] Ошибка: {error}"
            )

            continue

        for result in results:

            link = result.get(
                "link",
                ""
            )

            if not link:
                continue

            found[link] = result

    return list(found.values())[:limit]
