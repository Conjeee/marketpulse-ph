import asyncio
import structlog
from marketpulse import settings
from marketpulse.domain import Ticker

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

async def main():
    logger.info("pipeline_started", env=settings.ENVIRONMENT)
    logger.info("stock_loaded", count=len(Ticker))

    """
    Next steps will go here
    """

    logger.info("pipeline_finished")


if __name__ == "__main__":
    asyncio.run(main())