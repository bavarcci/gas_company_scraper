"""
==========================================================
exporter.py

Database Exporter

Exports records to:

    - Excel
    - CSV
    - JSON

Author: Ali Ba'varcci
==========================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd

from database.models import CompanyRecord


class ExcelExporter:

    def __init__(self):

        pass

    # ---------------------------------------------------------

    def save(self, records: Iterable, output_file):

        rows = []

        for record in records:

            if isinstance(record, CompanyRecord):

                rows.append(record.to_dict())

            else:

                rows.append(record)

        df = pd.DataFrame(rows)

        if df.empty:

            print("No records to export.")

            return

        self._reorder_columns(df)

        output_file = Path(output_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with pd.ExcelWriter(
            output_file,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Companies"
            )

            worksheet = writer.sheets["Companies"]

            for column_cells in worksheet.columns:

                length = max(

                    len(str(cell.value))
                    if cell.value is not None
                    else 0

                    for cell in column_cells

                )

                worksheet.column_dimensions[
                    column_cells[0].column_letter
                ].width = min(length + 3, 60)

        print(f"Excel exported: {output_file}")

    # ---------------------------------------------------------

    def save_csv(self, records, output_file):

        rows = []

        for record in records:

            if isinstance(record, CompanyRecord):

                rows.append(record.to_dict())

            else:

                rows.append(record)

        df = pd.DataFrame(rows)

        output_file = Path(output_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        df.to_csv(

            output_file,

            index=False,

            encoding="utf-8-sig"

        )

        print(f"CSV exported: {output_file}")

    # ---------------------------------------------------------

    def save_json(self, records, output_file):

        rows = []

        for record in records:

            if isinstance(record, CompanyRecord):

                rows.append(record.to_dict())

            else:

                rows.append(record)

        output_file = Path(output_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(

            output_file,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                rows,

                f,

                indent=4,

                ensure_ascii=False

            )

        print(f"JSON exported: {output_file}")

    # ---------------------------------------------------------

    def _reorder_columns(self, df):

        preferred = [

            "Company Name",

            "Country",

            "City",

            "Product Category",

            "Products",

            "Production Capacity",

            "Website",

            "Email",

            "Phone",

            "Address",

            "Contact Page",

            "LinkedIn",

            "Facebook",

            "Instagram",

            "X",

            "Source",

            "Quality Score",

        ]

        columns = [

            c

            for c in preferred

            if c in df.columns

        ]

        remaining = [

            c

            for c in df.columns

            if c not in columns

        ]

        df = df[columns + remaining]

        return df