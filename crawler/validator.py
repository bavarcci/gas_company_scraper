"""
==========================================================
validator.py

Data Quality Validator
Author: Ali Ba'varcci
==========================================================
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import validators
from email_validator import validate_email, EmailNotValidError


class DataValidator:

    def __init__(self):
        # Match the keys used in the pipeline
        self.required_fields = ["name", "country", "website"]

    def validate(self, record: dict) -> bool:
        self.clean(record)

        # Check required fields
        if not self.check_required(record):
            return False

        # Validate website and set flag
        self.validate_website(record)

        # Validate emails &/or phones
        self.validate_email(record)
        self.validate_phone(record)

        score = self.quality_score(record)
        record["Quality Score"] = score

        return score >= 20

    def clean(self, record):
        for key, value in record.items():
            if isinstance(value, str):
                value = re.sub(r"\s+", " ", value)
                record[key] = value.strip()

    def check_required(self, record):
        for field in self.required_fields:
            value = record.get(field, "")
            if not value:
                return False
        return True

    def validate_website(self, record):
        website = record.get("website", "")
        if not website:
            record["Website Valid"] = False
            return

        # Add scheme if missing
        if not website.startswith(("http://", "https://")):
            website = "https://" + website
            record["website"] = website

        if validators.url(website):
            record["Website Valid"] = True
        else:
            record["Website Valid"] = False

    def validate_email(self, record):
        emails = record.get("Email", "")
        if not emails:
            record["Valid Emails"] = ""
            return

        valid = []
        for email in emails.split(";"):
            email = email.strip()
            if not email:
                continue
            try:
                validate_email(email, check_deliverability=False)
                valid.append(email)
            except EmailNotValidError:
                pass

        record["Valid Emails"] = "; ".join(valid)

    def validate_phone(self, record):
        phones = record.get("Phone", "")
        cleaned = []
        for phone in phones.split(";"):
            phone = phone.strip()
            if len(phone) >= 6:
                cleaned.append(phone)
        record["Valid Phones"] = "; ".join(cleaned)

    def quality_score(self, record):
        score = 0

        if record.get("name"):
            score += 20
        if record.get("country"):
            score += 10
        if record.get("Website Valid"):
            score += 20
        if record.get("Valid Emails"):
            score += 20
        if record.get("Valid Phones"):
            score += 15
        if record.get("Address"):
            score += 10
        if record.get("Product Category"):
            score += 5

        return score