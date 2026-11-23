#!/usr/bin/env python3
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import time

def hit(url):
    start = time.perf_counter()
    try:
        with urlopen(url, timeout=5) as response:
            response.read()
            return response.status, time.perf_counter() - start
    except HTTPError as exc:
        return exc.code, time.perf_counter() - start
    except URLError:
        return 0, time.perf_counter() - start

def main():
    parser = argparse.ArgumentParser(description="Small standard-library HTTP load generator")
    parser.add_argument("--url", default="http://localhost:8000/api/orders")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()

    started = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(hit, args.url) for _ in range(args.requests)]
        for future in as_completed(futures):
            results.append(future.result())

    elapsed = time.perf_counter() - started
    successes = sum(1 for status, _ in results if 200 <= status < 400)
    failures = len(results) - successes
    latencies = sorted(lat for _, lat in results)
    p95 = latencies[min(len(latencies)-1, int(0.95 * len(latencies)))] if latencies else 0
    print(f"Requests: {len(results)} | success: {successes} | non-2xx/3xx: {failures}")
    print(f"Elapsed: {elapsed:.2f}s | throughput: {len(results)/elapsed:.2f} req/s | p95: {p95:.3f}s")

if __name__ == "__main__":
    main()
