"""
spider.py
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@dataclass
class Page:
    url: str
    html: str
    status_code: int


def parse_html(html: str) -> BeautifulSoup:
    """
    Parse HTML with a fallback parser.
    Tries lxml first (faster), then falls back to built-in html.parser.
    """
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        # lxml might be missing or fail on broken HTML
        return BeautifulSoup(html, "html.parser")


class WebsiteCrawler:
    def __init__(
        self,
        timeout: int = 30,
        max_pages: int = 20,
        max_depth: int = 2,
        user_agent: str = (
            "Mozilla/5.0 "
            "CompanyResearchBot/1.0"
        ),
    ):
        self.timeout = timeout
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.user_agent = user_agent

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )
    def _fetch(self, client: httpx.Client, url: str):
        """Fetch a URL with retries on HTTP errors."""
        return client.get(url)

    def crawl(self, start_url: str):
        domain = urlparse(start_url).netloc

        robot = RobotFileParser()
        robot.set_url(urljoin(start_url, "/robots.txt"))
        try:
            robot.read()
        except Exception:
            robot = None

        visited = set()
        pages = []
        queue = deque([(start_url, 0)])
        headers = {"User-Agent": self.user_agent}

        with httpx.Client(
            timeout=self.timeout,
            follow_redirects=True,
            headers=headers,
        ) as client:

            while queue and len(pages) < self.max_pages:
                url, depth = queue.popleft()

                # Skip if already visited or not a valid HTTP(S) URL
                if url in visited or not url.startswith(("http://", "https://")):
                    continue
                visited.add(url)

                if robot and not robot.can_fetch(self.user_agent, url):
                    continue

                try:
                    response = self._fetch(client, url)
                except Exception:
                    # Retries exhausted or other error
                    continue

                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type:
                    continue

                # Store the page
                pages.append(Page(
                    url=url,
                    html=response.text,
                    status_code=response.status_code,
                ))

                if depth >= self.max_depth:
                    continue

                soup = parse_html(response.text)

                for link in soup.find_all("a", href=True):
                    href = link["href"].strip()
                    if not href:
                        continue

                    absolute = urljoin(url, href)
                    parsed = urlparse(absolute)

                    if parsed.netloc != domain:
                        continue

                    # Removes query and fragment
                    absolute = urljoin(absolute, parsed.path)  # removes query and fragment

                    if absolute not in visited:
                        queue.append((absolute, depth + 1))

        return pages