import requests

from philawatch.constants import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN


def send_telegram_msg(message: str | None = None, file: str | None = None):
    if TELEGRAM_CHAT_ID is None or TELEGRAM_TOKEN is None:
        print(f"Telegram not setup. Not seending {message}")

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

    if file:
        with open(file, "rb") as f:
            _ = requests.post(
                url + f"/sendPhoto?chat_id={TELEGRAM_CHAT_ID}", files={"photo": f}
            )
    if message:
        _ = requests.post(
            url + f"/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
        )
