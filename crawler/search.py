"""
search.py

Company discovery from public sources.
Supports:
- SerpAPI
- Google scraping fallback
"""

from __future__ import annotations

import os
import time
import random
import logging
from dataclasses import dataclass, asdict
from typing import Iterable, List, Optional
from urllib.parse import quote_plus, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Blocklist for known non‑company domainz
# -------------------------------------------------------------------
BLOCKED_DOMAINS = {
    "offshore-technology.com",
    "ensun.io",
    "earabicmarket.com",
    "prospeo.io",
    "scribd.com",
    "youtube.com",
    "go4worldbusiness.com",
    "trademo.com",
    "arounddeal.com",
    "a-leads.co",
    "pnturkey.com",
    "qdb.qa",
    "qatarfactories.qa",
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "wikipedia.org",
    "wikimedia.org",
    "gov.ru",
    "blogspot.com",
    "wordpress.com",
    "medium.com",
    "reddit.com",
    "slideshare.net",
    "issuu.com",
    "calameo.com",
    "yandex.ru",
    "google.com",
    "mail.ru",
    "rambler.ru",
    "market.yandex.ru",
    "avito.ru",
}


BLOCKED_PATTERNS = [
    "news",
    "directory",
    "listing",
    "catalog",
    "database",
    "register",
    "marketplace",
]


def _is_company_website(url: str) -> bool:
    """
    Returns True if the URL is likely a company website (not a directory/news site).
    """
    if not url:
        return False
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    # Remove www prefix for comparison
    if domain.startswith("www."):
        domain = domain[4:]

    # Check exact blocklist
    if domain in BLOCKED_DOMAINS:
        return False
    # Check if any blocked pattern is in the domain
    if any(pattern in domain for pattern in BLOCKED_PATTERNS):
        return False

    # Optional: reject URLs with very deep paths (like /sector/theme/...)
    # but keep this simple; we'll rely on blocklist.

    return True


@dataclass
class Company:
    name: str
    country: str
    website: str = ""
    source: str = ""
    city: str = ""


class BaseSearchProvider:
    """Base class for all search providers."""

    def search(self, country: str, keywords: List[str], max_results: int = 10) -> List[Company]:
        raise NotImplementedError


class SerpApiProvider(BaseSearchProvider):
    """
    Uses SerpAPI (https://serpapi.com) to get Google search results.
    Requires an API key: SERPAPI_KEY.
    """

    def __init__(self, api_key: Optional[str] = None, max_searches: int = 100, timeout: int = 60):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            logger.warning("SERPAPI_KEY not set. SerpApiProvider will not work.")
        self.max_searches = max_searches
        self.searches_used = 0
        self.timeout = timeout

    def _check_quota(self, response: requests.Response) -> bool:
        """
        Check SerpAPI quota headers.
        Returns True if we can still make requests, False if quota is exhausted.
        """
        remaining = response.headers.get("X-API-Usage-Remaining")
        if remaining is not None:
            try:
                remaining = int(remaining)
                self.searches_used = self.max_searches - remaining
                if remaining <= 0:
                    logger.error("SerpAPI quota exhausted. Stopping further requests.")
                    return False
            except ValueError:
                pass
        if self.searches_used >= self.max_searches:
            logger.error(f"Reached configured max_searches ({self.max_searches}). Stopping.")
            return False
        return True

    def search(self, country: str, keywords: List[str], max_results: int = 10) -> List[Company]:
        if not self.api_key:
            logger.error("SerpAPI key missing. Skipping search.")
            return []
        companies = []
        for kw in keywords:
            if self.searches_used >= self.max_searches:
                logger.warning(f"Quota exhausted ({self.searches_used}/{self.max_searches}). Stopping searches for {country}.")
                break

            query = f"{kw} {country}"
            params = {
                "api_key": self.api_key,
                "engine": "google",
                "q": query,
                "num": min(max_results, 10),  # Set to 10 to save quota
                "gl": country_code(country),   # Country code
            }
            try:
                resp = requests.get("https://serpapi.com/search", params=params, timeout=self.timeout)
                resp.raise_for_status()

                if not self._check_quota(resp):
                    break

                data = resp.json()
                organic = data.get("organic_results", [])
                for result in organic:
                    name = result.get("title")
                    website = result.get("link")
                    if not name or not website:
                        continue

                    if not _is_company_website(website):
                        logger.debug(f"Skipping blocked domain: {website}")
                        continue

                    companies.append(Company(
                        name=name,
                        country=country,
                        website=website,
                        source="SerpAPI"
                    ))
                # Increment usage count
                self.searches_used += 1
                time.sleep(1)
            except Exception as e:
                logger.error(f"SerpAPI error for {query}: {e}")

        # Deduplicate by website
        seen = set()
        unique = []
        for c in companies:
            if c.website not in seen:
                seen.add(c.website)
                unique.append(c)
        logger.info(f"Used {self.searches_used} SerpAPI searches for {country}. Returning {len(unique)} companies.")
        return unique[:max_results]


class GoogleScrapeProvider(BaseSearchProvider):
    """
    Scrapes Google search results directly
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, delay: float = 2.0, timeout: int = 60):
        self.delay = delay
        self.timeout = timeout

    def _random_ua(self):
        return random.choice(self.USER_AGENTS)

    def search(self, country: str, keywords: List[str], max_results: int = 10) -> List[Company]:
        companies = []
        for kw in keywords:
            query = f"{kw} {country}"
            url = f"https://www.google.com/search?q={quote_plus(query)}&num={min(max_results, 100)}"
            headers = {"User-Agent": self._random_ua()}
            try:
                resp = requests.get(url, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for g in soup.find_all("div", class_="g"):
                    link = g.find("a", href=True)
                    if not link:
                        continue
                    website = link["href"]
                    if website.startswith("/url?q="):
                        website = website.split("/url?q=")[1].split("&")[0]
                    title = g.find("h3")
                    name = title.get_text() if title else website
                    if not name or not website:
                        continue

                    # Filter out non‑company websites
                    if not _is_company_website(website):
                        logger.debug(f"Skipping blocked domain: {website}")
                        continue

                    companies.append(Company(
                        name=name,
                        country=country,
                        website=website,
                        source="GoogleScrape"
                    ))
                time.sleep(self.delay + random.uniform(0, 1))
            except Exception as e:
                logger.error(f"Scrape error for {query}: {e}")

        # Deduplicate
        seen = set()
        unique = []
        for c in companies:
            if c.website not in seen:
                seen.add(c.website)
                unique.append(c)
        return unique[:max_results]


def country_code(country: str) -> str:
    """Map country name to Google country code (gl parameter)."""
    mapping = {
        "Russia": "ru",
    }
    return mapping.get(country, "")


class CompanySearcher:
    """
    Discovers companies using registered providers.
    If no providers are given, it uses SerpApiProvider if API key exists,
    otherwise falls back to GoogleScrapeProvider (with a warning).
    """

    def __init__(self, providers: Optional[List[BaseSearchProvider]] = None):
        if providers is None:
            if os.getenv("SERPAPI_KEY"):
                providers = [SerpApiProvider()]
                logger.info("Using SerpApiProvider for company search.")
            else:
                logger.warning("SERPAPI_KEY not set. Falling back to GoogleScrapeProvider (unreliable).")
                providers = [GoogleScrapeProvider()]
        self.providers = providers

    def register(self, provider: BaseSearchProvider):
        self.providers.append(provider)

    def search(self, country: str, keywords: List[str], max_results_per_keyword: int = 10) -> List[dict]:
        """
        Search for companies using all registered providers.
        Returns a list of dicts (compatible with the pipeline).
        """
        all_companies = []
        for provider in self.providers:
            try:
                results = provider.search(country, keywords, max_results_per_keyword)
                all_companies.extend(results)
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed: {e}")

        # Convert to dicts and deduplicate ***
        records = [asdict(c) for c in all_companies]
        return self._deduplicate(records)

    @staticmethod
    def _deduplicate(records: List[dict]) -> List[dict]:
        seen = set()
        unique = []
        for record in records:
            key = (
                record["name"].strip().lower(),
                record.get("website", "").strip().lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(record)
        return unique