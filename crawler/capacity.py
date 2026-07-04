"""
==========================================================
capacity.py

Production Capacity Extractor
==========================================================
"""

import re

from crawler.spider import parse_html   # fallback parser


class CapacityExtractor:

    def __init__(self):
        self.patterns = [

            # 120000 tons/year
            re.compile(
                r"([\d,\.]+)\s*(?:tons?|tonnes?)\s*(?:/|per)?\s*(?:year|yr|annum)",
                re.IGNORECASE
            ),

            # 120000 MT/year
            re.compile(
                r"([\d,\.]+)\s*MT\s*(?:/|per)?\s*(?:year|yr)",
                re.IGNORECASE
            ),

            # 5000 t/year
            re.compile(
                r"([\d,\.]+)\s*t\s*(?:/|per)?\s*(?:year|yr)",
                re.IGNORECASE
            ),

            # 250 KTPA
            re.compile(
                r"([\d,\.]+)\s*KTPA",
                re.IGNORECASE
            ),

            # 1.5 MTPA
            re.compile(
                r"([\d,\.]+)\s*MTPA",
                re.IGNORECASE
            ),

            # 2 million tons
            re.compile(
                r"([\d,\.]+)\s*million\s*tons?",
                re.IGNORECASE
            ),

            # annual capacity: 120000
            re.compile(
                r"annual\s+capacity[^0-9]{0,20}([\d,\.]+)",
                re.IGNORECASE
            ),

            # production capacity: 120000
            re.compile(
                r"production\s+capacity[^0-9]{0,20}([\d,\.]+)",
                re.IGNORECASE
            ),

            # capacity: 5000 tons (new pattern)
            re.compile(
                r"capacity[^0-9]{0,10}([\d,\.]+)\s*(?:tons?|tonnes?|MT)",
                re.IGNORECASE
            ),

            # annual production 200,000 MT
            re.compile(
                r"annual\s+production[^0-9]{0,20}([\d,\.]+)\s*(?:tons?|MT)",
                re.IGNORECASE
            ),
        ]

    # -------------------------------------------------

    def extract(self, pages):
        capacities = set()   # use set for deduplication

        for page in pages:
            soup = parse_html(page.html)   # fallback parser
            text = soup.get_text(separator=" ", strip=True)

            found = self.find_capacities(text)
            capacities.update(found)

        # Sort for consistent output
        sorted_capacities = sorted(capacities, key=lambda x: float(x.replace(',', '')) if x.replace(',', '').replace('.', '').isdigit() else 0, reverse=True)

        return {
            "Production Capacity": "; ".join(sorted_capacities)
        }

    # -------------------------------------------------

    def find_capacities(self, text):
        results = []

        for pattern in self.patterns:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                match = str(match).strip()
                # Clean up: remove commas, keep only digits and dots
                clean = re.sub(r'[^\d.]', '', match)
                if clean and len(clean) > 0:
                    results.append(clean)

        return results