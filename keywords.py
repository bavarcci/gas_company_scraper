"""
==========================================================
keywords.py

Natural Gas Industry Keywords (Russian Focus)
==========================================================
"""

# ==========================================================
# Core Industry & Company Keywords (Russian-specific)
# ==========================================================

INDUSTRY_KEYWORDS = [
    "Gazprom",
    "Novatek",
    "Rosneft gas",
    "Lukoil gas",
    "Surgutneftegas",
    "Tatneft",
    "Transneft",
    "gas field development Russia",
    "LNG plant Russia",
    "gas processing plant Russia",
    "gas pipeline operator Russia",
    "underground gas storage Russia",
    "gas production Russia",
    "natural gas producer Russia",
    "газовая компания Россия",          
    "Газпром",  
    "Новатэк", 
    "Роснефть газ",
    "газодобывающая компания",
]

# ==========================================================
# Raw Materials & Products (keep minimal)
# ==========================================================

RAW_MATERIAL_KEYWORDS = [
    "LNG",
    "CNG",
    "natural gas liquids",
    "condensate",
]

# ==========================================================
# Processing & Infrastructure (keep specific)
# ==========================================================

PROCESS_KEYWORDS = [
    "gas liquefaction",
    "regasification",
    "gas transmission",
    "compressor station",
    "gas terminal",
]

# ==========================================================
# Product Categories (keep focused)
# ==========================================================

PRODUCT_KEYWORDS = [
    "liquefied natural gas",
    "pipeline gas",
    "ethane",
    "propane",
    "helium",
]

# ==========================================================
# Infrastructure (reuse list for storage/hubs)
# ==========================================================

RECYCLING_KEYWORDS = [
    "gas storage",
    "LNG terminal",
    "gas hub",
]

# ==========================================================
# Services (keep minimal)
# ==========================================================

RUBBER_KEYWORDS = [
    "gas engineering",
    "gas equipment",
]

# ==========================================================
# Complete Search Keywords (manual curated list)
# ==========================================================

SEARCH_KEYWORDS = sorted(list(set(

    INDUSTRY_KEYWORDS
    + RAW_MATERIAL_KEYWORDS
    + PROCESS_KEYWORDS
    + PRODUCT_KEYWORDS
    + RECYCLING_KEYWORDS
    + RUBBER_KEYWORDS

)))
