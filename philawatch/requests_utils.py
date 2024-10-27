import time
from requests.exceptions import RequestException
import requests
from logging import getLogger


LOGGER = getLogger(__name__)


def make_request_with_retries(
    url: str, headers: dict[str, str], max_retries: int = 3, initial_delay: int = 1
) -> requests.Response | None:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except RequestException as e:
            if attempt < max_retries - 1:
                delay = initial_delay * (2**attempt)
                LOGGER.warning(f"Connection error: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                LOGGER.error(f"Failed to connect after {max_retries} attempts: {e}")
    return None
