# """
# ==========================================================
# Gas Company Intelligence Scraper
# Level-2 Market Intelligence Pipeline

# Author: Ali B'avarcci
# ==========================================================
# """

# import logging
# from pathlib import Path

# from crawler.search import CompanySearcher
# from crawler.spider import WebsiteCrawler
# # from crawler.products import ProductClassifier
# # from crawler.capacity import CapacityExtractor
# # from crawler.contact import ContactExtractor
# # from crawler.validator import DataValidator

# from database.exporter import ExcelExporter
# from database.deduplicate import remove_duplicates

# from config import (
#     COUNTRIES,
#     SEARCH_KEYWORDS,
#     OUTPUT_FILE,
#     MAX_COMPANIES
# )


# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s"
# )

# logger = logging.getLogger(__name__)


# class Pipeline:

#     def __init__(self):

#         self.searcher = CompanySearcher()
#         self.crawler = WebsiteCrawler()

#         self.contact = ContactExtractor()
#         self.product = ProductClassifier()
#         self.capacity = CapacityExtractor()

#         self.validator = DataValidator()

#         self.records = []

#     def discover_companies(self):

#         logger.info("===================================")
#         logger.info("Discovering companies...")
#         logger.info("===================================")

#         companies = []

#         for country in COUNTRIES:

#             logger.info(f"Searching in {country}")

#             results = self.searcher.search(
#                 country=country,
#                 keywords=SEARCH_KEYWORDS
#             )

#             companies.extend(results)

#         logger.info(f"Discovered {len(companies)} companies")

#         return companies[:MAX_COMPANIES]

#     def crawl_company(self, company):

#         logger.info(f"Crawling {company['name']}")

#         website = company.get("website")

#         if not website:
#             return None

#         pages = self.crawler.crawl(website)

#         record = company.copy()

#         ###############################
#         # Contact
#         ###############################

#         record.update(
#             self.contact.extract(pages)
#         )

#         ###############################
#         # Products
#         ###############################

#         record.update(
#             self.product.extract(pages)
#         )

#         ###############################
#         # Production Capacity
#         ###############################

#         record.update(
#             self.capacity.extract(pages)
#         )

#         ###############################
#         # Validation
#         ###############################

#         if not self.validator.validate(record):
#             return None

#         return record

#     def run(self):

#         companies = self.discover_companies()

#         logger.info("")
#         logger.info(f"Processing {len(companies)} companies")
#         logger.info("")

#         for company in companies:

#             try:

#                 record = self.crawl_company(company)

#                 if record:

#                     self.records.append(record)

#                     logger.info(
#                         f"Collected {record['name']}"
#                     )

#             except Exception as e:

#                 logger.error(e)

#         logger.info("")
#         logger.info("Removing duplicates...")

#         self.records = remove_duplicates(self.records)

#         logger.info(
#             f"Final database contains {len(self.records)} companies"
#         )

#         exporter = ExcelExporter()

#         exporter.save(
#             self.records,
#             OUTPUT_FILE
#         )

#         logger.info("")
#         logger.info("Finished Successfully.")
#         logger.info(f"Saved to {OUTPUT_FILE}")


# def ensure_directories():

#     Path("output").mkdir(exist_ok=True)
#     Path("cache").mkdir(exist_ok=True)
#     Path("logs").mkdir(exist_ok=True)


# def main():

#     ensure_directories()

#     pipeline = Pipeline()

#     pipeline.run()


# if __name__ == "__main__":
#     main()

"""
==========================================================
config.py

Configuration File

Natural Gas Industry in Russia Intelligence Scraper

Author: Ali Ba'varcci
==========================================================
"""

from pathlib import Path

###########################################################
# PATHS
###########################################################

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / "cache"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_FILE = OUTPUT_DIR / "companies.xlsx"

###########################################################
# PROJECT SETTINGS
###########################################################

PROJECT_NAME = "Plastic & Polymer Company Intelligence"

MAX_COMPANIES = 1500

MAX_PAGES_PER_WEBSITE = 20

MAX_DEPTH = 2

REQUEST_TIMEOUT = 20

HEADLESS = True

###########################################################
# CONCURRENCY
###########################################################

MAX_CONCURRENT_SITES = 5

###########################################################
# RETRY
###########################################################

RETRY_COUNT = 3

RETRY_DELAY = 2

###########################################################
# USER AGENT
###########################################################

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/138.0 Safari/537.36"
)

###########################################################
# COUNTRIES
###########################################################

COUNTRIES = ["Russia"]
MAX_COMPANIES = 50   # reduce to avoid wasting time on many low-quality results
SEARCH_KEYWORDS = [
    "natural gas producer",
    "gas processing plant",
    "oil and gas company",
    "gas field development",
    "liquefied natural gas",
    "gas pipeline",
    "gas exploration",
    "gas refining",
    "petrochemical gas",
    "gas compression",
    "gas treatment",
    "gas transmission",
    "gas storage",
]

###########################################################
# PRODUCT CATEGORIES
###########################################################

PRODUCT_CATEGORIES = {

    "Polyethylene": [
        "polyethylene",
        "pe",
        "hdpe",
        "ldpe",
        "lldpe",
    ],

    "Polypropylene": [
        "polypropylene",
        "pp",
    ],

    "PVC": [
        "pvc",
    ],

    "PET": [
        "pet",
    ],

    "ABS": [
        "abs",
    ],

    "Polycarbonate": [
        "polycarbonate",
        "pc",
    ],

    "Packaging": [
        "packaging",
        "film",
        "bag",
        "container",
    ],

    "Pipes": [
        "pipe",
        "pipes",
        "tube",
    ],

    "Masterbatch": [
        "masterbatch",
    ],

    "Compounds": [
        "compound",
        "compounds",
    ],

    "Recycling": [
        "recycling",
        "recycled",
    ],

}

###########################################################
# REGEX
###########################################################

EMAIL_REGEX = (
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

PHONE_REGEX = (
    r"(\+\d[\d\s\-\(\)]{7,}\d)"
)