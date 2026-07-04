"""
==========================================================
deduplicate.py

Duplicate Detection Module

Author: Ali Ba'varcci
==========================================================
"""

from urllib.parse import urlparse

from rapidfuzz import fuzz


# ---------------------------------------------------------
# Normalize Company Name
# ---------------------------------------------------------

COMPANY_SUFFIXES = [

    "co",

    "co.",

    "company",

    "ltd",

    "ltd.",

    "llc",

    "inc",

    "corporation",

    "corp",

    "group",

    "holding",

    "factory",

    "industries",

    "industry",

]


def normalize_name(name: str):

    if not name:

        return ""

    name = name.lower()

    for suffix in COMPANY_SUFFIXES:

        name = name.replace(suffix, "")

    name = " ".join(name.split())

    return name.strip()


# ---------------------------------------------------------
# Extract Website Domain
# ---------------------------------------------------------

def get_domain(url):

    if not url:

        return ""

    try:

        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):

            domain = domain[4:]

        return domain

    except Exception:

        return ""


# ---------------------------------------------------------
# Email Domain
# ---------------------------------------------------------

def email_domain(email):

    if not email:

        return ""

    email = email.split(";")[0].strip()

    if "@" not in email:

        return ""

    return email.split("@")[-1].lower()


# ---------------------------------------------------------
# Similarity Score
# ---------------------------------------------------------

def similarity(a, b):

    return fuzz.token_sort_ratio(a, b)


# ---------------------------------------------------------
# Duplicate Detection
# ---------------------------------------------------------

def is_duplicate(record1, record2):

    name1 = normalize_name(

        record1.get("Company Name", "")

    )

    name2 = normalize_name(

        record2.get("Company Name", "")

    )

    domain1 = get_domain(

        record1.get("Website", "")

    )

    domain2 = get_domain(

        record2.get("Website", "")

    )

    if domain1 and domain2:

        if domain1 == domain2:

            return True

    email1 = email_domain(

        record1.get("Email", "")

    )

    email2 = email_domain(

        record2.get("Email", "")

    )

    if email1 and email2:

        if email1 == email2:

            return True

    score = similarity(

        name1,

        name2

    )

    if score >= 92:

        return True

    return False


# ---------------------------------------------------------
# Remove Duplicates
# ---------------------------------------------------------

def remove_duplicates(records):

    unique = []

    for record in records:

        duplicate = False

        for existing in unique:

            if is_duplicate(

                record,

                existing

            ):

                duplicate = True

                break

        if not duplicate:

            unique.append(record)

    return unique