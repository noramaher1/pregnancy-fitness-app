"""Sends many requests to the gateway so the autoscaler has something to react to.

Usage: python loadtest.py http://localhost:8080 --threads 30 --seconds 180
"""
import argparse
import threading
import time
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("base_url")
parser.add_argument("--threads", type=int, default=30)
parser.add_argument("--seconds", type=int, default=180)
args = parser.parse_args()

url = args.base_url.rstrip("/") + "/api/overview?user=loadtest&week=20"
stop_at = time.time() + args.seconds
lock = threading.Lock()
stats = {"ok": 0, "errors": 0, "total_time": 0.0}


def worker():
    while time.time() < stop_at:
        start = time.time()
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                r.read()
            ok = True
        except (urllib.error.URLError, TimeoutError, OSError):
            ok = False
        elapsed = time.time() - start
        with lock:
            stats["ok" if ok else "errors"] += 1
            stats["total_time"] += elapsed


threads = [threading.Thread(target=worker) for _ in range(args.threads)]
for t in threads:
    t.start()
while any(t.is_alive() for t in threads):
    time.sleep(10)
    with lock:
        done = stats["ok"] + stats["errors"]
        print(f"requests: {done}  errors: {stats['errors']}")
for t in threads:
    t.join()
done = stats["ok"] + stats["errors"]
avg = stats["total_time"] / done if done else 0
print(f"finished: {done} requests, {stats['errors']} errors, average {avg * 1000:.0f} ms")
