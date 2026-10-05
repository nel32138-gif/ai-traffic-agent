import asyncio
import argparse
from agent import run_agent


def main():
    parser = argparse.ArgumentParser(
        description="AI agent for finding potential clients"
    )

    parser.add_argument(
        "request",
        help='Например: "Найди 10 потенциальных клиентов на баннеры в Telegram"'
    )

    args = parser.parse_args()

    asyncio.run(run_agent(args.request))


if __name__ == "__main__":
    main()
