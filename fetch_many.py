from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import Sequence

from dotenv import load_dotenv
import httpx

logger = logging.getLogger("fetch_many")

DEFAULT_URLS: list[str] = [
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/posts/2",
    "https://jsonplaceholder.typicode.com/posts/3",
]


@dataclass(slots=True)
class Result:
    url: str
    status: int | None
    elapsed_ms: float
    ok: bool


async def fetch_one(client: httpx.AsyncClient, url: str) -> Result:
    start = time.perf_counter()
    try:
        resp = await client.get(url)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info("%s -> %s (%.1f ms)", url, resp.status_code, elapsed)
        return Result(url, resp.status_code, elapsed, resp.status_code < 400)
    except httpx.HTTPError as exc:
        elapsed = (time.perf_counter() - start) * 1000
        logger.warning("%s 请求失败: %s", url, exc)
        return Result(url, None, elapsed, False)


async def fetch_all(urls: Sequence[str], timeout: float) -> list[Result]:
    headers = {"User-Agent": "redrock-task1/0.1"}
    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
        return await asyncio.gather(*(fetch_one(client, u) for u in urls))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="并发请求多个 HTTP 接口并汇总结果")
    parser.add_argument("urls", nargs="*", help="要请求的 URL，不填则用内置示例")
    parser.add_argument("--timeout", type=float,
                        default=float(os.getenv("REQUEST_TIMEOUT", "10")))
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    urls = args.urls or DEFAULT_URLS
    t0 = time.perf_counter()
    results = asyncio.run(fetch_all(urls, args.timeout))
    total = (time.perf_counter() - t0) * 1000

    for r in results:
        print(f"{'OK ' if r.ok else 'ERR'} {str(r.status):>4} {r.elapsed_ms:8.1f}ms  {r.url}")
    ok = sum(r.ok for r in results)
    print(f"\n共 {len(results)} 个接口，成功 {ok} 个，总耗时 {total:.1f} ms")
    raise SystemExit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()