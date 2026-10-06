import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs, unquote


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/18.0 Mobile/15E148 Safari/604.1"
    )
}


def extract_terms(request):
    text = request.lower()

    if "баннер" in text or "banner" in text:
        return [
            "нужен баннер",
            "нужны баннеры",
            "нужен дизайнер",
            "ищем дизайнера",
            "ищу дизайнера",
            "заказать баннер",
            "дизайн рекламы",
            "рекламный креатив",
            "креатив для рекламы",
            "оформление рекламы",
        ]

    if "сайт" in text or "лендинг" in text:
        return [
            "нужен сайт",
            "нужен лендинг",
            "ищем веб дизайнера",
            "нужен веб дизайнер",
            "заказать сайт",
        ]

    if "видео" in text or "монтаж" in text:
        return [
            "нужен монтаж видео",
            "ищем монтажера",
            "нужен видеомонтаж",
            "нужен видеограф",
        ]

    if "логотип" in text:
        return [
            "нужен логотип",
            "ищем дизайнера логотипа",
            "заказать логотип",
        ]

    words = re.findall(
        r"[A-Za-zА-Яа-яЁё0-9_-]{4,}",
        text
    )

    return words[:8]


def get_real_url(href):
    if not href:
        return ""

    if href.startswith("//"):
        href = "https:" + href

    # DuckDuckGo иногда отдаёт redirect URL.
    parsed = urlparse(href)

    if "duckduckgo.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if "uddg" in query:
            return unquote(query["uddg"][0])

    return href


def search_duckduckgo(query, limit=30):
    url = (
        "https://html.duckduckgo.com/html/?q="
        + quote(query)
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    results = []

    for result in soup.select(".result"):

        link_tag = result.select_one(
            ".result__a"
        )

        if not link_tag:
            continue

        href = get_real_url(
            link_tag.get("href", "")
        )

        title = link_tag.get_text(
            " ",
            strip=True
        )

        snippet_tag = result.select_one(
            ".result__snippet"
        )

        snippet = (
            snippet_tag.get_text(
                " ",
                strip=True
            )
            if snippet_tag
            else ""
        )

        if "t.me/" not in href:
            continue

        results.append({
            "name": title,
            "link": href,
            "text": snippet
        })

        if len(results) >= limit:
            break

    return results


async def telegram_search(request, limit=100):

    terms = extract_terms(request)

    print(
        "[SEARCH] Ключевые запросы:"
    )

    for term in terms:
        print(f"  - {term}")

    found = {}

    for term in terms:

        query = f'site:t.me "{term}"'

        print(
            f"[SEARCH] Ищу: {query}"
        )

        try:

            results = search_duckduckgo(
                query,
                limit=30
            )

            print(
                f"[SEARCH] Получено результатов: "
                f"{len(results)}"
            )

        except Exception as error:

            print(
                f"[SEARCH] Ошибка поиска: {error}"
            )

            continue

        for result in results:

            link = result.get(
                "link",
                ""
            ).strip()

            if not link:
                continue

            found[link] = result

    results = list(found.values())

    print(
        f"[SEARCH] Уникальных Telegram-источников: "
        f"{len(results)}"
    )

    return results[:limit]
