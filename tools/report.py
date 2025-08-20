#!python
# -*- coding: utf-8 -*-

import datetime
import json
import os
import sys
from pprint import pprint

import pandas as pd

sys.path.insert(0, os.getcwd())

from src import const, rok_profile
from src.const import PROJECT_ROOT
from src.element import ResourceAmount, ResourceSet, TaxRate
from src.task import Report


def format_dataframe_for_display(df, resource_columns=None):
    """
    Create a formatted version of DataFrame that uses ResourceAmount.__str__() for display.

    Args:
        df: pandas DataFrame
        resource_columns: list of column names containing ResourceAmount objects
                         If None, defaults to ["food", "wood", "stone", "gold"]

    Returns:
        DataFrame with ResourceAmount objects converted to their string representation
    """
    if resource_columns is None:
        resource_columns = ["food", "wood", "stone", "gold"]

    df_display = df.copy()
    for col in resource_columns:
        if col in df_display.columns:
            df_display[col] = df[col].apply(lambda x: str(x) if hasattr(x, "__str__") else x)

    return df_display


profile = rok_profile.RokProfile()
chars = profile.chars

_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
# rss.json is a general file for all char_id
rss_file = const.RSS_PATH
if not os.path.exists(rss_file):
    print("rss.json not found")
    sys.exit(1)

with open(rss_file, "r", encoding="utf-8") as f:
    rss_data = json.load(f)

rows = []
for char_id, rss in rss_data.items():
    char = profile.chars.get(char_id)
    if char is None:
        # char_id in rss.json but not in profile.yaml → skip
        continue
    avail = ResourceSet.from_dict(rss["avail_rss"])
    tax = TaxRate.from_ch(char.ch)
    rows.append(
        {
            "name": char.name,
            "ch": char.ch,
            "tax": tax,
            "food": avail.food,
            "gold": avail.gold,
            "stone": avail.stone,
            "wood": avail.wood,
        }
    )

# Create DataFrame with rows data
# Use dtype='object' for resource columns to preserve ResourceAmount type
df = pd.DataFrame(rows, dtype="object")

# Optional: order columns explicitly
df = df[["name", "ch", "tax", "food", "wood", "stone", "gold"]]
for col in ["food", "wood", "stone", "gold"]:
    df[f"{col}_after_tax"] = df.apply(lambda row: row[col].after_tax(row["tax"]), axis=1)

# Use pandas .sum() and convert results back to ResourceAmount
totals = df[[f"{col}_after_tax" for col in ["food", "wood", "stone", "gold"]]].sum()

# Build the summary row - convert float totals back to ResourceAmount
summary_row = {
    "name": "TOTAL (AFTER TAX)",
    "ch": "",
    "tax": "",
    "food": ResourceAmount(totals["food_after_tax"]),
    "wood": ResourceAmount(totals["wood_after_tax"]),
    "stone": ResourceAmount(totals["stone_after_tax"]),
    "gold": ResourceAmount(totals["gold_after_tax"]),
}

# Append row to df
df_with_total = df.drop(
    columns=["food_after_tax", "wood_after_tax", "stone_after_tax", "gold_after_tax"]
)
df_with_total = pd.concat(
    [df_with_total, pd.DataFrame([summary_row], dtype="object")], ignore_index=True
)

# Display final report with totals
print("\nFinal Report with Totals:")
print(format_dataframe_for_display(df_with_total).to_string(index=False))
# Save DataFrame with totals to CSV
output_path = PROJECT_ROOT / "tmp" / "record" / f"resources_after_tax_{_date_str}.csv"
df_with_total.to_csv(output_path, index=False, encoding="utf-8")

print(f"Saved to {output_path}")
