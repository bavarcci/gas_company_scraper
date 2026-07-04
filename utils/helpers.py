"""
==========================================================
utils/helpers.py

General Utility Functions

Author: Ali Derakhshan
==========================================================
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from urllib.parse import urlparse


# ==========================================================
# String Utilities
# ==========================================================

def clean_text(text: str) -> str:
    """
    Remove extra spaces and line breaks.
    """

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# URL Utilities
# ==========================================================

def normalize_url(url: str) -> str:
    """
    Normalize URL.
    """

    if not url:

        return ""

    url = url.strip()

    if not url.startswith(("http://", "https://")):

        url = "https://" + url

    return url


def get_domain(url: str) -> str:
    """
    Return domain without www.
    """

    if not url:

        return ""

    try:

        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):

            domain = domain[4:]

        return domain

    except Exception:

        return ""


# ==========================================================
# Email Utilities
# ==========================================================

def normalize_email(email: str) -> str:

    if not email:

        return ""

    return email.strip().lower()


# ==========================================================
# Phone Utilities
# ==========================================================

def normalize_phone(phone: str) -> str:

    if not phone:

        return ""

    phone = phone.replace(" ", "")

    phone = phone.replace("-", "")

    phone = phone.replace("(", "")

    phone = phone.replace(")", "")

    return phone


# ==========================================================
# Address Utilities
# ==========================================================

def clean_address(address: str) -> str:

    if not address:

        return ""

    address = clean_text(address)

    address = address.replace(" ,", ",")

    return address


# ==========================================================
# Hash Utilities
# ==========================================================

def md5(text: str) -> str:

    return hashlib.md5(

        text.encode("utf-8")

    ).hexdigest()


# ==========================================================
# Time Utilities
# ==========================================================

def timestamp():

    return datetime.utcnow().isoformat()


# ==========================================================
# Company Name Utilities
# ==========================================================

COMPANY_SUFFIXES = [

    "co",

    "co.",

    "company",

    "ltd",

    "ltd.",

    "llc",

    "inc",

    "corp",

    "corporation",

    "group",

    "factory",

    "industries",

    "industry",

]


def normalize_company_name(name: str):

    if not name:

        return ""

    name = name.lower()

    for suffix in COMPANY_SUFFIXES:

        name = name.replace(suffix, "")

    return clean_text(name)


# ==========================================================
# Safe Dictionary Getter
# ==========================================================

def safe_get(dictionary, key, default=""):

    value = dictionary.get(key, default)

    if value is None:

        return default

    return value


# ==========================================================
# List Utilities
# ==========================================================

def unique(items):

    seen = set()

    result = []

    for item in items:

        if item not in seen:

            seen.add(item)

            result.append(item)

    return result


# ==========================================================
# File Size
# ==========================================================

def human_size(size):

    for unit in ["B", "KB", "MB", "GB"]:

        if size < 1024:

            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} TB"