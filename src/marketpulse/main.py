import asyncio
import structlog
from marketpulse import settings
from marketpulse.services import run_ingestion

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

async def main():
    logger.info("pipeline_started", env=settings.ENVIRONMENT)
    logger.info("ingestion_started", batch_size=30)
    
    raw_data_batch = await run_ingestion()
    successful_fetches = [data for data in raw_data_batch if data.get("price") is not None]
    
    logger.info(
        "ingestion_completed",
        total_attempted=len(raw_data_batch),
        successful=len(successful_fetches)
    )
    
    if successful_fetches:
        print(f"\nSample Data Extracted: {successful_fetches[0]}\n")
        
if __name__ == "__main__":
    asyncio.run(main())