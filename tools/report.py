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


def get_rss_data(data):  # Accept "total_rss" or "avail_rss" as string
    avail_rss = []
    total_rss = []
    for char_id, rss in data.items():
        char = profile.chars.get(char_id)
        if char is None:
            # char_id in rss.json but not in profile.yaml → skip
            continue
        avail = ResourceSet.from_dict(rss["avail_rss"])
        total = ResourceSet.from_dict(rss["total_rss"])
        tax = TaxRate.from_ch(char.ch)
        avail_rss.append(
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
        total_rss.append(
            {
                "name": char.name,
                "ch": char.ch,
                "tax": tax,
                "food": total.food,
                "gold": total.gold,
                "stone": total.stone,
                "wood": total.wood,
            }
        )
    return avail_rss, total_rss


def create_resource_dataframe(rss_data):
    # Create DataFrame with rows data
    # Use dtype='object' for resource columns to preserve ResourceAmount type
    df = pd.DataFrame(rss_data, dtype="object")

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
    return df_with_total


def report_df(df, title):
    # Display final report with totals
    print(f"\n{title}:")
    print(format_dataframe_for_display(df).to_string(index=False))


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

avail_rss, total_rss = get_rss_data(rss_data)
avail_df = create_resource_dataframe(avail_rss)
total_df = create_resource_dataframe(total_rss)

report_df(avail_df, "Available Resources")
report_df(total_df, "Total Resources")

# Create a separator row with dashes
separator_row = {col: "----------" for col in avail_df.columns}
separator_df = pd.DataFrame([separator_row])

# Combine both dataframes with the separator
combined_df = pd.concat([avail_df, separator_df, total_df], ignore_index=True)

# Save combined dataframe to CSV
output_path = PROJECT_ROOT / "tmp" / "record" / f"resources_{_date_str}.csv"
combined_df.to_csv(output_path, index=False, encoding="utf-8")
print(f"Saved combined resources to {output_path}")
