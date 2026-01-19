#!/usr/bin/env python3
import itertools
import json
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib.error


def normalize_domain(domain):
    domain = domain.strip()
    if domain.startswith("http://"):
        domain = domain[len("http://") :]
    elif domain.startswith("https://"):
        domain = domain[len("https://") :]
    if "/" in domain:
        domain = domain.split("/", 1)[0]
    domain = domain.strip(".")
    if not domain:
        return ""
    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        pass
    return domain.lower()


def fetch_subdomains(domain, max_retries=3, timeout=30):
    query = f"%.{domain}"
    params = urllib.parse.urlencode({"q": query, "output": "json"})
    url = f"https://crt.sh/?{params}"
    last_exc = None
    for attempt in range(1, max_retries + 1):
        request = urllib.request.Request(url, headers={"User-Agent": "crt-subdomains/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8", errors="replace")
            data = json.loads(payload)
            break
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if 500 <= exc.code < 600 and attempt < max_retries:
                time.sleep(0.8 * attempt)
                continue
            raise
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            last_exc = exc
            if attempt < max_retries:
                time.sleep(0.8 * attempt)
                continue
            raise
    else:
        if last_exc is not None:
            raise last_exc
    names = set()
    for entry in data:
        name_value = entry.get("name_value", "")
        for name in name_value.splitlines():
            name = name.strip().lower()
            if not name:
                continue
            if name.startswith("*."):
                name = name[2:]
            if name == domain or name.endswith("." + domain):
                names.add(name)
    return sorted(names)


class Spinner:
    def __init__(self, message, stream=sys.stderr, interval=0.1):
        self.message = message
        self.stream = stream
        self.interval = interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)

    def _spin(self):
        for ch in itertools.cycle("|/-\\"):
            if self._stop.is_set():
                break
            self.stream.write(ch)
            self.stream.flush()
            time.sleep(self.interval)
            self.stream.write("\b")
            self.stream.flush()

    def __enter__(self):
        self.stream.write(f"{self.message} ")
        self.stream.flush()
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self._stop.set()
        self._thread.join()
        self.stream.write(" \n")
        self.stream.flush()
        return False


def main():
    try:
        raw_domain = input("Enter domain: ").strip()
    except EOFError:
        return 1
    domain = normalize_domain(raw_domain)
    if not domain:
        print("No domain provided.", file=sys.stderr)
        return 1
    try:
        with Spinner("Задача принята. Идет выполнение."):
            subdomains = fetch_subdomains(domain)
    except Exception as exc:
        print(f"crt.sh request failed: {exc}", file=sys.stderr)
        return 2
    if not subdomains:
        print("No subdomains found.")
        return 0
    for name in subdomains:
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
