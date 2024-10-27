from datetime import datetime
import random
import time
from philawatch import telegram
from philawatch.models import Event
from typing import Any
import click
from logging import getLogger

from philawatch.requests_utils import make_request_with_retries

LOGGER = getLogger(__name__)


def find_event(name: str) -> Event | None:
    url = "https://bourseauxbillets.philharmoniedeparis.fr/list/resale/resaleProductCatalog.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.3"
    }

    response = make_request_with_retries(url, headers)
    if response is None:
        return None

    try:
        events = response.json()["topicWithProductsList"][0]["products"]
    except Exception:
        LOGGER.exception(f"Can't process data: {response.text}")
        return None

    return find_matching_event(events, name)


def find_matching_event(events: list[dict[str, Any]], name: str) -> Event | None:
    for event_json in events:
        event = Event.from_json(event_json)
        if name in event.name.lower():
            return event
    return None


def check_tickets_event(
    name: str, min_tickets: int, wanted_dates: list[datetime]
) -> Event | None:
    event = find_event(name=name)

    if not event:
        LOGGER.warning(f"No event found with name: {name}.")
        return None

    LOGGER.debug(f"Found matching event: {event.name}!")

    if event.available_quantity < min_tickets:
        LOGGER.debug(
            f"Only {event.available_quantity} tickets available, need {min_tickets}"
        )
        return None

    if wanted_dates and not any(
        wanted_date in event.dates for wanted_date in wanted_dates
    ):
        LOGGER.debug(f"No tickets for dates {wanted_dates}")
        return None

    return event


@click.command()
@click.option(
    "--name",
    help="Event name (or keyword)",
    required=True,
)
@click.option("--min-tickets", help="Minimum number of tickets", default=1)
@click.option(
    "--dates", help="Wanted dates for ticekts: YYYY-MM-DD,YYYY-MM-DD", default=None
)
def search_tickets(name: str, min_tickets: int, dates: str | None) -> None:
    dates_datetime: list[datetime] = []
    if dates:
        for date_str in dates.split(","):
            date = datetime.strptime(date_str, "%Y-%m-%d")
            dates_datetime.append(date)

    while True:
        event = check_tickets_event(
            name=name.lower(), min_tickets=min_tickets, wanted_dates=dates_datetime
        )

        if event:
            LOGGER.info(event.found_message())
            telegram.send_telegram_msg(event.found_message())
            return

        time.sleep(random.randint(20, 40))


if __name__ == "__main__":
    search_tickets()
