import os
import json
from dotenv import load_dotenv

from search import telegram_search
from analyzer import rank_candidates

load_dotenv()


async def run_agent(request: str):
    wanted = int(os.getenv("RESULTS", "10"))
    limit = int(os.getenv("SEARCH_LIMIT", "150"))

    print(f"\n[AGENT] Запрос: {request}")

    print("[1/3] Ищу потенциальных клиентов...")
    candidates = await telegram_search(request, limit=limit)

    if not candidates:
        print("Ничего не найдено.")
        return

    print(f"[2/3] Найдено кандидатов: {len(candidates)}")

    ranked = await rank_candidates(request, candidates)

    ranked = ranked[:wanted]

    print(f"[3/3] Лучшие {len(ranked)} кандидатов:\n")

    for i, candidate in enumerate(ranked, 1):
        print(f"{i}. {candidate.get('name', 'Без названия')}")
        print(f"   Ссылка: {candidate.get('link', '—')}")
        print(f"   Оценка: {candidate.get('score', 0)}/100")
        print(f"   Почему: {candidate.get('reason', '—')}")
        print(f"   Сигнал: {candidate.get('signal', '—')}")
        print()

    with open("results.json", "w", encoding="utf-8") as file:
        json.dump(
            ranked,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("Результаты сохранены в results.json")
