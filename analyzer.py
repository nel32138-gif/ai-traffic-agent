import os
import json
import asyncio

from dotenv import load_dotenv

load_dotenv()


def local_score(candidate):
    text = (candidate.get("text") or "").lower()

    score = 15

    positive_signals = [
        "нужен дизайнер",
        "ищем дизайнера",
        "нужен баннер",
        "нужны баннеры",
        "заказать дизайн",
        "нужен дизайн",
        "ищу дизайнера",
        "требуется дизайнер",
        "рекламный баннер",
        "реклама",
        "креатив",
        "оформление",
        "запуск рекламы",
    ]

    negative_signals = [
        "ищу работу дизайнером",
        "вакансия дизайнера",
        "я дизайнер",
        "услуги дизайнера",
        "портфолио дизайнера",
    ]

    for signal in positive_signals:
        if signal in text:
            score += 10

    for signal in negative_signals:
        if signal in text:
            score -= 15

    if candidate.get("username"):
        score += 5

    score = max(0, min(100, score))

    return score


async def rank_candidates(request, candidates):

    api_key = os.getenv("GEMINI_API_KEY")

    # Если AI API пока не подключён,
    # агент всё равно работает.
    if not api_key:

        for candidate in candidates:

            candidate["score"] = local_score(candidate)

            candidate["reason"] = (
                "Найден сигнал потенциальной потребности "
                "в услуге."
            )

            candidate["signal"] = (
                candidate.get("text") or ""
            ).replace("\n", " ")[:200]

        return sorted(
            candidates,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

    try:

        import google.generativeai as genai

        genai.configure(
            api_key=api_key
        )

        model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )

        prompt = """
Ты квалифицируешь потенциальных клиентов.

Задача:
определить, какие найденные Telegram-сообщения
могут принадлежать потенциальным покупателям услуги.

Не выдумывай информацию.

Особенно важно:
- покупатель услуги должен отличаться от исполнителя;
- человек, который ищет дизайнера, потенциально подходит;
- дизайнер, который продаёт свои услуги, не подходит;
- обычная реклама без признака потребности имеет низкий балл.

Верни ТОЛЬКО JSON-массив.

Для каждого кандидата используй:

name
link
score
reason
signal

score от 0 до 100.
"""

        prompt += "\n\nЗапрос пользователя:\n"
        prompt += request

        prompt += "\n\nКандидаты:\n"

        prompt += json.dumps(
            candidates[:80],
            ensure_ascii=False
        )

        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )

        text = response.text.strip()

        text = text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        result = json.loads(text)

        return sorted(
            result,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

    except Exception as error:

        print(
            f"[AI] Ошибка AI-анализа: {error}"
        )

        print(
            "[AI] Использую локальную оценку."
        )

        for candidate in candidates:

            candidate["score"] = local_score(
                candidate
            )

            candidate["reason"] = (
                "Локальная оценка потенциальной "
                "потребности."
            )

            candidate["signal"] = (
                candidate.get("text") or ""
            ).replace("\n", " ")[:200]

        return sorted(
            candidates,
            key=lambda x: x.get("score", 0),
            reverse=True
        )
