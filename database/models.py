"""
==========================================================
models.py

Database Models

Author: Ali Ba'varcci
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional


# ==========================================================
# Company Record
# ==========================================================

@dataclass
class CompanyRecord:

    # -----------------------------
    # Basic Information
    # -----------------------------

    company_name: str = ""
    country: str = ""
    city: str = ""

    # -----------------------------
    # Products
    # -----------------------------

    product_category: str = ""
    products: List[str] = field(default_factory=list)

    production_capacity: str = ""

    # -----------------------------
    # Contact Information
    # -----------------------------

    website: str = ""
    email: List[str] = field(default_factory=list)
    phone: List[str] = field(default_factory=list)
    address: str = ""

    contact_page: str = ""

    # -----------------------------
    # Social Media
    # -----------------------------

    linkedin: str = ""
    facebook: str = ""
    instagram: str = ""
    x: str = ""

    # -----------------------------
    # Metadata
    # -----------------------------

    source: str = ""

    quality_score: int = 0

    website_valid: bool = False

    crawl_date: Optional[str] = None

    # --------------------------------------------------

    def to_dict(self):

        data = asdict(self)

        data["products"] = "; ".join(self.products)

        data["email"] = "; ".join(self.email)

        data["phone"] = "; ".join(self.phone)

        return data


# ==========================================================
# Crawl Statistics
# ==========================================================

@dataclass
class CrawlStatistics:

    companies_discovered: int = 0

    companies_processed: int = 0

    successful_records: int = 0

    failed_records: int = 0

    duplicate_records: int = 0

    crawl_time_seconds: float = 0.0

    # --------------------------------------------------

    def success_rate(self):

        if self.companies_processed == 0:

            return 0.0

        return round(

            self.successful_records
            / self.companies_processed
            * 100,

            2

        )


# ==========================================================
# Export Metadata
# ==========================================================

@dataclass
class ExportInfo:

    project_name: str

    output_file: str

    total_records: int

    generated_at: str

    exporter_version: str = "1.0"

    author: str = "Ali Derakhshan"