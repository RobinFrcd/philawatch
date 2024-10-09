import logging
from rich.logging import RichHandler

FORMAT = "%(name)s - %(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logging.getLogger("urllib3").setLevel("WARNING")
