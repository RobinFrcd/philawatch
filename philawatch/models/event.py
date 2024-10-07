from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Event:
    name: str
    dates: list[datetime]
    available_quantity: int
    min_price: float
    product_page: str

    @staticmethod
    def from_json(json_data: dict[str, Any]):
        dates: list[datetime] = list()
        int_dates_list: list[list[int]] = json_data.get("availablePerfDate", [])

        for date_list in int_dates_list:
            date = datetime(year=date_list[0], month=date_list[1], day=date_list[2])
            dates.append(date)

        return Event(
            name=str(json_data.get("name", "")),
            dates=dates,
            available_quantity=int(json_data.get("availableQuantity", -1)),
            min_price=round(float(json_data.get("minPrice", -1000)) / 1000, 2),
            product_page=json_data.get("productPagePath", ""),
        )

    def found_message(self) -> str:
        return f"""Event for {self.name} found.
Dates: {', '.join([d.strftime("%c") for d in self.dates])}.
Number of tickets: {self.available_quantity} at {self.min_price}EUR.
Link: https://bourseauxbillets.philharmoniedeparis.fr{self.product_page}"""
