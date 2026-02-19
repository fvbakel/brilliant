#!/usr/bin/env python3
"""
Link‑checker voor een website (incl. externe links).

Gebruik:
    python link_checker.py https://example.com
"""

import sys
import time
import urllib.parse
from collections import deque

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------
# Configuratie
# ----------------------------------------------------------------------
TIMEOUT = 10               # seconden per request
MAX_PAGES = 500            # maximale aantal interne pagina's om te crawlen
SLEEP_BETWEEN_REQUESTS = 0.2  # korte pauze om de server niet te overbelasten
USER_AGENT = "LumoLinkChecker/1.0 (+https://lumo.proton.me)"


def fetch(url):
    """Doe een HEAD‑request; val terug op GET als HEAD niet wordt ondersteund."""
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.head(url, allow_redirects=True,
                             timeout=TIMEOUT, headers=headers)
        # Sommige servers antwoorden niet op HEAD → probeer GET
        if resp.status_code == 405:          # Method Not Allowed
            resp = requests.get(url, allow_redirects=True,
                                timeout=TIMEOUT, headers=headers, stream=True)
        return resp
    except requests.RequestException as e:
        return None, str(e)


def extract_links(html, base_url):
    """Geef een set van absolute URLs terug die in de HTML staan."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        # negeer lege of javascript‑links en mailto links
        if not href \
           or href.startswith("#") \
           or href.lower().startswith("mailto:") \
           or href.lower().startswith("javascript:"):
            continue
        # maak relatieve URL's absoluut
        absolute = urllib.parse.urljoin(base_url, href)
        links.add(absolute.split('#')[0])   # verwijder fragment‑identifier
    return links


def is_internal(url, domain):
    """Is de URL binnen hetzelfde domein (intern)?"""
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc == domain


def crawl(start_url):
    """Crawl de site en verzamel alle interne pagina‑URL's."""
    parsed_start = urllib.parse.urlparse(start_url)
    domain = parsed_start.netloc

    visited = set()
    to_visit = deque([start_url])
    internal_pages = set()

    while to_visit and len(internal_pages) < MAX_PAGES:
        url = to_visit.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = requests.get(url, timeout=TIMEOUT,
                                headers={"User-Agent": USER_AGENT})
            if resp.status_code != 200:
                print(f"[WARN] {url} returned {resp.status_code}")
                continue
        except requests.RequestException as e:
            print(f"[ERROR] Could not fetch {url}: {e}")
            continue

        internal_pages.add(url)
        links = extract_links(resp.text, url)

        for link in links:
            if is_internal(link, domain) and link not in visited:
                to_visit.append(link)

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return internal_pages


def check_links(pages):
    """Controleer alle links (intern én extern) en rapporteer fouten."""
    broken = []      # (link, status / error, bronpagina)
    seen = set()     # voorkom dubbele checks

    for page in pages:
        try:
            print(f"Checking page {page}")
            resp = requests.get(page, timeout=TIMEOUT,
                                headers={"User-Agent": USER_AGENT})
            html = resp.text
        except requests.RequestException as e:
            print(f"[ERROR] Could not fetch page {page}: {e}")
            continue

        links = extract_links(html, page)
        print(f"Found {len(links)} links, checking links")

        for link in links:
            if link in seen:
                continue
            seen.add(link)

            try:
                r = requests.head(link, allow_redirects=True,
                                  timeout=TIMEOUT,
                                  headers={"User-Agent": USER_AGENT})

                if r.status_code == 405:
                    r = requests.get(link, allow_redirects=True,
                                     timeout=TIMEOUT,
                                     headers={"User-Agent": USER_AGENT},
                                     stream=True)
                status = r.status_code
            except requests.RequestException as e:
                print(f"Broken link found: [{link}]")
                broken.append((link, f"Request error: {e}", page))
                continue

            if status == 404:
                print(f"Broken link found: [{link}]")
                broken.append((link, f"404 Not Found", page))
            elif status >= 400:
                print(f"Broken link found: [{link}]")
                broken.append((link, f"{status} Error", page))

            time.sleep(SLEEP_BETWEEN_REQUESTS)

    return broken


def main():
    if len(sys.argv) != 2:
        print("Usage: python link_checker.py <start-url>")
        sys.exit(1)

    start_url = sys.argv[1]
    print(f"Crawlen van {start_url} …")
    pages = crawl(start_url)
    print(f"\nGevonden {len(pages)} interne pagina('s). Nu links controleren…\n")

    broken_links = check_links(pages)

    if not broken_links:
        print("✅ Geen gebroken links gevonden!")
    else:
        print(f"⚠️ {len(broken_links)} gebroken link(s) gevonden:")
        for link, reason, src in broken_links:
            print(f"- {link} ({reason}) – gevonden op {src}")


if __name__ == "__main__":
    main()