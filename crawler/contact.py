"""
contact.py

Extract contact information from downloaded HTML pages.

Author: Ali Ba'varcci
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import phonenumbers
from bs4 import BeautifulSoup

from config import EMAIL_REGEX, PHONE_REGEX
from crawler.spider import parse_html   # import the fallback parser


class ContactExtractor:

    def __init__(self):
        self.email_pattern = re.compile(EMAIL_REGEX, re.IGNORECASE)
        self.phone_pattern = re.compile(PHONE_REGEX)

    # -----------------------------------------------------

    def extract(self, pages):
        emails = set()
        phones = set()
        address = ""
        contact_page = ""
        linkedin = ""
        facebook = ""
        instagram = ""
        x = ""

        for page in pages:
            # Use the fallback parser
            soup = parse_html(page.html)

            text = soup.get_text(" ", strip=True)

            # ----------------------------
            # Emails
            # ----------------------------
            for email in self.email_pattern.findall(text):
                # clean up common garbage
                email = email.strip().lower()
                if '@' in email and len(email) < 100:
                    emails.add(email)

            for link in soup.find_all("a", href=True):
                href = link["href"].strip()
                if href.startswith("mailto:"):
                    email = href.replace("mailto:", "").split("?")[0].strip().lower()
                    if email:
                        emails.add(email)

            # ----------------------------
            # Phones
            # ----------------------------
            for phone in self.phone_pattern.findall(text):
                normalized = self.normalize_phone(phone)
                if normalized:
                    phones.add(normalized)

            # ----------------------------
            # Contact page
            # ----------------------------
            if not contact_page:
                for link in soup.find_all("a", href=True):
                    href = link["href"].lower()
                    if any(key in href for key in ["contact", "contact-us", "contacts", "contactus"]):
                        contact_page = page.url
                        break

            # ----------------------------
            # Social media
            # ----------------------------
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "linkedin.com" in href:
                    # prefer full profile/company URLs
                    if "company" in href or "pub" in href or "in/" in href:
                        linkedin = href
                    elif not linkedin:  # fallback
                        linkedin = href
                elif "facebook.com" in href:
                    if not facebook:
                        facebook = href
                elif "instagram.com" in href:
                    if not instagram:
                        instagram = href
                elif "twitter.com" in href or "x.com" in href:
                    if not x:
                        x = href

            # ----------------------------
            # Address
            # ----------------------------
            if not address:
                address = self.extract_address(soup)

        return {
            "Email": "; ".join(sorted(emails)),
            "Phone": "; ".join(sorted(phones)),
            "Address": address,
            "Contact Page": contact_page,
            "LinkedIn": linkedin,
            "Facebook": facebook,
            "Instagram": instagram,
            "X": x,
        }

    # -----------------------------------------------------

    def normalize_phone(self, phone):
        phone = phone.strip()
        try:
            parsed = phonenumbers.parse(phone, None)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            pass
        return phone

    # -----------------------------------------------------

    def extract_address(self, soup):
        candidates = []
        selectors = [
            "address",
            ".address",
            "#address",
            ".contact",
            ".footer",
            ".footer-contact",
            "[itemprop='address']",
            ".location",
            ".office",
            ".company-address",
        ]

        for selector in selectors:
            for node in soup.select(selector):
                txt = node.get_text(" ", strip=True)
                # Only keep reasonably long strings that look like addresses
                if len(txt) > 20 and any(word in txt.lower() for word in ["street", "road", "avenue", "blvd", "suite", "po box", "p.o.", "city", "state", "zip", "postal"]):
                    candidates.append(txt)

        if candidates:
            # Choose the longest one that is not too long (avoid huge blocks)
            best = max(candidates, key=len)
            # Clean up extra spaces and newlines
            best = re.sub(r'\s+', ' ', best).strip()
            return best

        return ""


# """
# crawler/contact.py

# Extract contact information from downloaded HTML pages.
# """

# from __future__ import annotations

# import re
# from urllib.parse import urlparse

# import phonenumbers
# from bs4 import BeautifulSoup

# from config import EMAIL_REGEX, PHONE_REGEX


# class ContactExtractor:

#     def __init__(self):

#         self.email_pattern = re.compile(
#             EMAIL_REGEX,
#             re.IGNORECASE
#         )

#         self.phone_pattern = re.compile(
#             PHONE_REGEX
#         )

#     # -----------------------------------------------------

#     def extract(self, pages):

#         emails = set()
#         phones = set()

#         address = ""

#         contact_page = ""

#         linkedin = ""
#         facebook = ""
#         instagram = ""
#         x = ""

#         for page in pages:

#             soup = BeautifulSoup(page.html, "lxml")

#             text = soup.get_text(" ", strip=True)

#             # ----------------------------
#             # Emails
#             # ----------------------------

#             for email in self.email_pattern.findall(text):
#                 emails.add(email.lower())

#             for link in soup.find_all("a", href=True):

#                 href = link["href"].strip()

#                 if href.startswith("mailto:"):

#                     emails.add(
#                         href.replace(
#                             "mailto:",
#                             ""
#                         ).split("?")[0].lower()
#                     )

#             # ----------------------------
#             # Phones
#             # ----------------------------

#             for phone in self.phone_pattern.findall(text):

#                 phone = self.normalize_phone(phone)

#                 if phone:
#                     phones.add(phone)

#             # ----------------------------
#             # Contact page
#             # ----------------------------

#             if not contact_page:

#                 for link in soup.find_all("a", href=True):

#                     href = link["href"].lower()

#                     if any(
#                         key in href
#                         for key in [
#                             "contact",
#                             "contact-us",
#                             "contacts",
#                         ]
#                     ):

#                         contact_page = page.url

#                         break

#             # ----------------------------
#             # Social media
#             # ----------------------------

#             for link in soup.find_all("a", href=True):

#                 href = link["href"]

#                 if "linkedin.com" in href:

#                     linkedin = href

#                 elif "facebook.com" in href:

#                     facebook = href

#                 elif "instagram.com" in href:

#                     instagram = href

#                 elif "twitter.com" in href or "x.com" in href:

#                     x = href

#             # ----------------------------
#             # Address
#             # ----------------------------

#             if not address:

#                 address = self.extract_address(soup)

#         return {

#             "Email": "; ".join(sorted(emails)),

#             "Phone": "; ".join(sorted(phones)),

#             "Address": address,

#             "Contact Page": contact_page,

#             "LinkedIn": linkedin,

#             "Facebook": facebook,

#             "Instagram": instagram,

#             "X": x,

#         }

#     # -----------------------------------------------------

#     def normalize_phone(self, phone):

#         phone = phone.strip()

#         try:

#             parsed = phonenumbers.parse(
#                 phone,
#                 None
#             )

#             if phonenumbers.is_valid_number(parsed):

#                 return phonenumbers.format_number(

#                     parsed,

#                     phonenumbers.PhoneNumberFormat.E164

#                 )

#         except Exception:

#             pass

#         return phone

#     # -----------------------------------------------------

#     def extract_address(self, soup):

#         candidates = []

#         selectors = [

#             "address",

#             ".address",

#             "#address",

#             ".contact",

#             ".footer",

#             ".footer-contact",

#         ]

#         for selector in selectors:

#             for node in soup.select(selector):

#                 txt = node.get_text(
#                     " ",
#                     strip=True
#                 )

#                 if len(txt) > 20:

#                     candidates.append(txt)

#         if candidates:

#             return max(candidates, key=len)

#         return ""