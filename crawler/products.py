"""
products.py

Product classification module
"""

from collections import Counter

from config import PRODUCT_CATEGORIES
from crawler.spider import parse_html   # fallback parser


class ProductClassifier:

    def __init__(self):
        self.categories = PRODUCT_CATEGORIES

    # -------------------------------------------------

    def extract(self, pages):
        text = self.collect_text(pages)

        category_hits = Counter()
        product_hits = []

        lower_text = text.lower()

        for category, keywords in self.categories.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches (optional)
                # Simple substring match (original behavior)
                if keyword.lower() in lower_text:
                    category_hits[category] += 1
                    product_hits.append(keyword.lower())  # store lowercased for consistency

        # Sort categories by hit count (descending)
        categories = sorted(
            category_hits,
            key=category_hits.get,
            reverse=True
        )

        # Unique product keywords (keep original casing? using lowercased)
        products = sorted(set(product_hits))

        return {
            "Product Category": "; ".join(categories),
            "Products": "; ".join(products),
            "Category Score": dict(category_hits)
        }

    # -------------------------------------------------

    def collect_text(self, pages):
        parts = []

        for page in pages:
            soup = parse_html(page.html)
            parts.append(
                soup.get_text(
                    separator=" ",
                    strip=True
                )
            )

        return " ".join(parts)