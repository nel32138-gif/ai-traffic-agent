import json
import re

from dotenv import load_dotenv

from search import telegram_search
from analyzer import rank_candidates

load_dotenv()


def parse_request(request):
    text = request.lower()

    number = 10

    match = re.search(r"\b(\d+)\b", text)

    if match:
        number = int(match.group(1))

    if "баннер" in text or "banner" in text:
        service = "баннеры"

    elif "дизайн" in text:
        service = "дизайн"

    elif "сайт" in text or "лендинг" in text:
        service = "создание сайтов"

    elif "видео" in text or "монтаж" in text:
        service = "монтаж видео"

    elif "логотип" in text:
        service = "логотипы"

    else:
        service = text

    return {
        "service": service,
        "number": number,
        "original_request": request
    }


async def run_agent(request):

    parsed = parse_request(request)

    wanted = parsed["number"]

    print()
    print("================================")
    print("       AI TRAFFIC AGENT")
    print("================================")
    print()

    print(
        f"[REQUEST] {parsed['original_request']}"
    )

    print(
        f"[SERVICE] {parsed['service']}"
    )

    print(
        f"[TARGET] {wanted} клиентов"
    )

    print()

    # -------------------------
    # SEARCH
    # -------------------------

    print(
        "[1/3] Ищу публичные Telegram-источники..."
    )

    try:

        candidates = await telegram_search(
            request,
            limit=100
        )

    except Exception as error:

        print(
            f"[SEARCH ERROR] {error}"
        )

        candidates = []

    print(
        f"[FOUND] Найдено источников: "
        f"{len(candidates)}"
    )

    print()

    # -------------------------
    # ANALYSIS
    # -------------------------

    if candidates:

        print(
            "[2/3] Анализирую кандидатов..."
        )

        try:

            ranked = await rank_candidates(
                request,
                candidates
            )

        except Exception as error:

            print(
                f"[AI ERROR] {error}"
            )

            ranked = candidates

    else:

        print(
            "[2/3] Кандидатов для анализа нет."
        )

        ranked = []

    # -------------------------
    # RESULTS
    # -------------------------

    ranked = ranked[:wanted]

    print()

    print(
        f"[3/3] Результатов: "
        f"{len(ranked)}"
    )

    print()

    if not ranked:

        print(
            "Пока не удалось найти подходящих "
            "потенциальных клиентов."
        )

    else:

        for index, candidate in enumerate(
            ranked,
            1
        ):

            print(
                f"{index}. "
                f"{candidate.get('name', 'Без названия')}"
            )

            print(
                f"   Ссылка: "
                f"{candidate.get('link', '—')}"
            )

            print(
                f"   Оценка: "
                f"{candidate.get('score', 0)}/100"
            )

            print(
                f"   Почему: "
                f"{candidate.get('reason', '—')}"
            )

            print(
                f"   Сигнал: "
                f"{candidate.get('signal', '—')}"
            )

            print()

    # -------------------------
    # ALWAYS CREATE RESULTS
    # -------------------------

    with open(
        "results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            ranked,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(
        "[DONE] results.json создан."
    )
