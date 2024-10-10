from datetime import datetime
import random
import time
from philawatch import telegram
from philawatch.models import Event
from typing import Any
import requests
import click
from logging import getLogger

LOGGER = getLogger(__name__)


def find_event(name: str) -> Event | None:
    req = requests.get(
        "https://bourseauxbillets.philharmoniedeparis.fr/list/resale/resaleProductCatalog.json",
        headers={
            "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.3"
        },
    )
    try:
        events: list[dict[str, Any]] = req.json()["topicWithProductsList"][0]["products"]
    except Exception:
        LOGGER.exception(f"Can't process data: {req.text}")
        return None

    for event_json in events:
        event = Event.from_json(event_json)

        if name in event.name.lower():
            return event


def check_tickets_event(name: str, min_tickets: int, wanted_dates: list[datetime]):
    event = find_event(name=name)

    if not event:
        LOGGER.warning(f"No event found with name: {name}.")
        return

    LOGGER.debug(f"Found matching event: {event.name}!")

    if event.available_quantity < min_tickets:
        LOGGER.debug(
            f"Only {event.available_quantity} tickets available, need {min_tickets}"
        )
        return

    if wanted_dates and not any(
        wanted_date in event.dates for wanted_date in wanted_dates
    ):
        LOGGER.debug(f"No tickets for dates {wanted_dates}")
        return

    return event


@click.command()
@click.option(
    "--name",
    help="Event name (or keyword)",
)
@click.option("--min-tickets", help="Minimum number of tickets", default=1)
@click.option(
    "--dates", help="Wanted dates for ticekts: YYYY-MM-DD,YYYY-MM-DD", default=None
)
def search_tickets(name: str, min_tickets: int, dates: str | None):
    dates_datetime: list[datetime] = []
    if dates:
        for date_str in dates.split(","):
            dates_numbers = [int(d) for d in date_str.split("-")]
            date = datetime(*dates_numbers)
            dates_datetime.append(date)

    while True:
        event = check_tickets_event(
            name=name.lower(), min_tickets=min_tickets, wanted_dates=dates_datetime
        )

        if event:
            print(event.found_message())
            telegram.send_telegram_msg(event.found_message())
            return

        time.sleep(random.randint(20, 40))


if __name__ == "__main__":
    search_tickets()
