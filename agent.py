import os
import json
from dotenv import load_dotenv

from search import telegram_search
from analyzer import rank_candidates

load_dotenv()


def parse_request(request):
    """
    Определяет количество клиентов, услугу
    и ключевые слова для поиска.
    """

    text = request.lower()

    # Количество
    number = 10

    import re

    match = re.search(
        r"\b(\d+)\b",
        text
    )

    if match:
        number = int(match.group(1))

    # Определяем услугу
    if "баннер" in text:
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


async def run_agent(request: str):

    parsed = parse_request(request)

    wanted = parsed["number"]

    print()
    print("================================")
    print("        AI TRAFFIC AGENT")
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

    # Поиск
    print(
        "[1/3] Ищу потенциальных клиентов..."
    )

    candidates = await telegram_search(
        request,
        limit=100
    )

    if not candidates:

        print(
            "Не удалось найти кандидатов."
        )

        return

    print(
        f"[FOUND] Найдено: {len(candidates)}"
    )

    print()

    # AI анализ
    print(
        "[2/3] Анализирую кандидатов..."
    )

    ranked = await rank_candidates(
        request,
        candidates
    )

    # Лучшие результаты
    ranked = ranked[:wanted]

    print()
    print(
        f"[3/3] Лучшие {len(ranked)} кандидатов:"
    )
    print()

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

    # Сохраняем результаты
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
        "Результаты сохранены в results.json"
    )
