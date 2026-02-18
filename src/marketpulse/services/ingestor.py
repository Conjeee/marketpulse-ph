import asyncio
import aiohttp
import yfinance as yf
import feedparser
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
from marketpulse.domain import Ticker

logger = structlog.get_logger()

# Retry 3 times, waits exponentially
retry_policy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=40),
    reraise=True
)


@retry_policy
def _get_yfinance_price(ticker_value: str) -> float:
    """
    Scrapes stock prices using yfinance. private.

    Args:
        ticker_value (str): Ticker of the stock from models.py

    Returns:
        float: Closing price of the stock
    """
    
    stock = yf.Ticker(ticker_value)
    hist = stock.history(period="1d")
    
    if hist.empty:
        raise ValueError(f"No price data found for {ticker_value}")
    
    return float(hist["Close"].iloc[-1])


async def fetch_price(ticker: Ticker) -> float | None:
    """
    Uses _get_yfinance_price to scrape price from yfinance and runs it in the background thread
    
    :param ticker: Ticker of the stock from models.py
    :type ticker: Ticker
    :return: returns the closing price of the stock in float or None
    :rtype: float | None
    """
    
    try:
        price = await asyncio.to_thread(_get_yfinance_price, ticker.value)
        
        logger.info("status", 
                    level="INFO", 
                    ticker=ticker.name, 
                    action="fetch_price", 
                    status="success"
                    )
        return price
    
    except Exception as e:
        logger.error("status", 
                     level="ERROR", 
                     ticker=ticker.name, 
                     action="fetch_price", 
                     error=type(e).__name__
                     )
        return None
    

@retry_policy
async def fetch_news(session: aiohttp.ClientSession, ticker: Ticker) -> str | None:
    """
    Fetches news asynchronously

    Args:
        session (aiohttp.ClientSession): Create a client session to pass all the links
        ticker (Ticker): Ticker of the stock from models.py

    Returns:
        str | None: latest news title of the ticker or None
    """
    
    try:
        url = f"https://news.google.com/rss/search?q={ticker.name}+stock+philippines&hl=en-PH&gl=PH&ceid=PH:en"
        
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            xml_data = await response.text()
            
        
        feed = feedparser.parse(xml_data)
        if feed.entries:
            latest_headline = feed.entries[0].title
            logger.info("status",
                        level="INFO",
                        ticker=ticker.name,
                        action="fetch_news",
                        status="success"
                        )
            
            return latest_headline
        
        return None
    
    except Exception as e:
        logger.error("status",
                     level="ERROR",
                     ticker=ticker.name,
                     action="fetch_news",
                     error=type(e).__name__
                     )
        
        return None
    

async def process_ticker(session: aiohttp.ClientSession, ticker: Ticker) -> dict:
    """
    Gathers price task and news task and returns a dictionary of information

    Args:
        session (aiohttp.ClientSession): Create a client session to pass all the links
        ticker (Ticker): Ticker of the stock from models.py

    Returns:
        dict: Ticker, latest closing price, and latest headline
    """
    
    price_task = fetch_price(ticker)
    news_task = fetch_news(session, ticker)
    
    price, news = await asyncio.gather(price_task, news_task)
    
    return {
        "ticker": ticker,
        "price": price,
        "news_headline": news
    }
    
async def run_ingestion() -> list[dict]:
    """
    Creates a task for every ticker and asynchronously runs them

    Returns:
        list[dict]: Ticker code, price and, headline of every stock ticker in Ticker
    """

    async with aiohttp.ClientSession() as session:
        tasks = [process_ticker(session, ticker) for ticker in Ticker]
        results = await asyncio.gather(*tasks)
        return results