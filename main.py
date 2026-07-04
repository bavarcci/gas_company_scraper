"""
==========================================================
Company Intelligence Scraper (Natural Gas / Russia)
Level-2 Market Intelligence Pipeline

Author: Ali Ba'varcci
==========================================================
"""

import logging
from pathlib import Path
from dotenv import load_dotenv   # load environment variables

load_dotenv()

from crawler.search import CompanySearcher
from crawler.spider import WebsiteCrawler
from crawler.products import ProductClassifier
from crawler.capacity import CapacityExtractor
from crawler.contact import ContactExtractor
from crawler.validator import DataValidator

from database.exporter import ExcelExporter
from database.deduplicate import remove_duplicates

from config import (
    COUNTRIES,
    SEARCH_KEYWORDS,
    OUTPUT_FILE,
    MAX_COMPANIES
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


class Pipeline:

    def __init__(self):
        # CompanySearcher will auto-configure: uses SerpApiProvider if SERPAPI_KEY exists,
        self.searcher = CompanySearcher()
        self.crawler = WebsiteCrawler()   # uses default timeout, max_pages & ...

        self.contact = ContactExtractor()
        self.product = ProductClassifier()
        self.capacity = CapacityExtractor()

        self.validator = DataValidator()

        self.records = []

    def discover_companies(self):
        logger.info("===================================")
        logger.info("Discovering companies...")
        logger.info("===================================")

        companies = []

        for country in COUNTRIES:
            logger.info(f"Searching in {country}")

            results = self.searcher.search(
                country=country,
                keywords=SEARCH_KEYWORDS
            )

            companies.extend(results)

        logger.info(f"Discovered {len(companies)} companies")
        return companies[:MAX_COMPANIES]

    def crawl_company(self, company):
        logger.info(f"Crawling {company['name']}")

        website = company.get("website")
        if not website:
            logger.warning(f"No website for {company['name']}, skipping.")
            return None

        pages = self.crawler.crawl(website)

        record = company.copy()

        # Extract contact info
        record.update(self.contact.extract(pages))

        # Extract product categories
        record.update(self.product.extract(pages))

        # Extract production capacity
        record.update(self.capacity.extract(pages))

        # Validate and compute Q score
        if not self.validator.validate(record):
            score = record.get("Quality Score", 0)
            name = record.get("name", "Unknown")
            # Print key fields for debugging
            print(f" FAILED: {name} (Score: {score})")
            print(f"   Email: {record.get('Email', '')[:50]}")
            print(f"   Phone: {record.get('Phone', '')[:50]}")
            print(f"   Product Category: {record.get('Product Category', '')[:50]}")
            print(f"   Website: {record.get('website', '')}")
            return None
        else:
            logger.info(f" PASSED: {record.get('name')} (Score: {record.get('Quality Score')})")

        return record

    def run(self):
        companies = self.discover_companies()

        if not companies:
            logger.warning("No companies discovered. Exiting.")
            return

        logger.info("")
        logger.info(f"Processing {len(companies)} companies")
        logger.info("")

        for company in companies:
            try:
                record = self.crawl_company(company)
                if record:
                    self.records.append(record)
                    logger.info(f"Collected {record['name']}")
            except Exception as e:
                logger.error(f"Error crawling {company.get('name', 'unknown')}: {e}")

        logger.info("")
        logger.info("Removing duplicates...")
        self.records = remove_duplicates(self.records)

        logger.info(f"Final database contains {len(self.records)} companies")

        if self.records:
            exporter = ExcelExporter()
            exporter.save(self.records, OUTPUT_FILE)
            logger.info("")
            logger.info("Finished Successfully.")
            logger.info(f"Saved to {OUTPUT_FILE}")
        else:
            logger.warning("No records to export.")


def ensure_directories():
    Path("output").mkdir(exist_ok=True)
    Path("cache").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)


def main():
    ensure_directories()
    pipeline = Pipeline()
    pipeline.run()


if __name__ == "__main__":
    main()