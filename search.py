import os
import re

from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()


def extract_terms(request):
    text = request.lower()

    terms = []

    if "баннер" in text or "banner" in text:
        terms += [
            "баннер",
            "баннеры",
            "дизайн",
            "реклама",
            "креатив",
        ]

    if "дизайн" in text:
        terms += [
            "дизайн",
            "дизайнер",
        ]

    if "сайт" in text:
        terms += [
            "сайт",
            "лендинг",
            "веб-дизайн",
        ]

    if not terms:
        terms = re.findall(
            r"[A-Za-zА-Яа-яЁё0-9_-]{4,}",
            text
        )[:8]

    return list(dict.fromkeys(terms))


async def telegram_search(request, limit=150):

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone = os.getenv("TELEGRAM_PHONE")

    if not api_id or not api_hash:
        raise RuntimeError(
            "Не заполнены TELEGRAM_API_ID и TELEGRAM_API_HASH"
        )

    client = TelegramClient(
        "agent_session",
        int(api_id),
        api_hash
    )

    await client.start(
        phone=phone or None
    )

    found = {}

    try:

        terms = extract_terms(request)

        print(f"[SEARCH] Ключевые запросы: {terms}")

        for term in terms:

            async for message in client.iter_messages(
                None,
                search=term,
                limit=limit
            ):

                if not message:
                    continue

                if not message.text:
                    continue

                if not message.chat:
                    continue

                chat = message.chat

                username = getattr(
                    chat,
                    "username",
                    None
                )

                title = (
                    getattr(chat, "title", None)
                    or username
                    or "Telegram"
                )

                if username:
                    link = f"https://t.me/{username}"
                else:
                    link = ""

                key = (
                    getattr(chat, "id", None),
                    message.id
                )

                found[key] = {
                    "name": title,
                    "username": username or "",
                    "link": link,
                    "text": message.text[:1800],
                    "message_id": message.id,
                    "date": (
                        message.date.isoformat()
                        if message.date
                        else ""
                    )
                }

    finally:

        await client.disconnect()

    return list(found.values())
