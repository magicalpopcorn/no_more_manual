#!python
# -*- coding: utf-8 -*-

import datetime
import json
import os
import sys
import traceback
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve() / ".." / ".."))
from src.lib import const, rok_profile
from src.lib.const import PROJECT_ROOT
from src.lib.element import ResourceAmount, ResourceSet, TaxRate


def format_dataframe_for_display(df):
    """
    Create a formatted version of DataFrame that uses ResourceAmount.__str__() for display.

    Args:
        df: pandas DataFrame
    Returns:
        DataFrame with ResourceAmount objects converted to their string representation
    """
    for col in ["Food", "Wood", "Stone", "Gold"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x) if hasattr(x, "__str__") else x)

    # return df


def get_rss_data(data):  # Accept "total_rss" or "avail_rss" as string
    profile = rok_profile.RokProfile()

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
                "Name": char.name,
                "CH": char.ch,
                "Tax": tax,
                "Food": avail.food,
                "Gold": avail.gold,
                "Stone": avail.stone,
                "Wood": avail.wood,
            }
        )
        total_rss.append(
            {
                "Name": char.name,
                "CH": char.ch,
                "Tax": tax,
                "Food": total.food,
                "Gold": total.gold,
                "Stone": total.stone,
                "Wood": total.wood,
            }
        )
    return avail_rss, total_rss


def create_resource_dataframe(rss_data):
    # Create DataFrame with rows data
    # Use dtype='object' for resource columns to preserve ResourceAmount type
    df = pd.DataFrame(rss_data, dtype="object")

    # Optional: order columns explicitly
    df = df[["Name", "CH", "Tax", "Food", "Wood", "Stone", "Gold"]]
    for col in ["Food", "Wood", "Stone", "Gold"]:
        df[f"{col}_after_tax"] = df.apply(lambda row: row[col].after_tax(row["Tax"]), axis=1)

    # Use pandas .sum() and convert results back to ResourceAmount
    totals = df[[f"{col}_after_tax" for col in ["Food", "Wood", "Stone", "Gold"]]].sum()

    # Build the summary row - convert float totals back to ResourceAmount
    summary_row = {
        "Name": "TOTAL (AFTER TAX)",
        "CH": "",
        "Tax": "",
        "Food": ResourceAmount(totals["Food_after_tax"]),
        "Wood": ResourceAmount(totals["Wood_after_tax"]),
        "Stone": ResourceAmount(totals["Stone_after_tax"]),
        "Gold": ResourceAmount(totals["Gold_after_tax"]),
    }

    # Append row to df
    df_with_total = df.drop(
        columns=["Food_after_tax", "Wood_after_tax", "Stone_after_tax", "Gold_after_tax"]
    )
    df_with_total = pd.concat(
        [df_with_total, pd.DataFrame([summary_row], dtype="object")], ignore_index=True
    )
    return df_with_total


def report_df(df, title):
    # Display final report with totals
    print(f"\n{title}:")
    print(df.to_string(index=False))


def process_rss():
    # rss.json is a general file for all char_id
    if not os.path.exists(const.RSS_PATH):
        print("rss.json not found")
        sys.exit(1)

    with open(const.RSS_PATH, "r", encoding="utf-8") as f:
        rss_data = json.load(f)

    avail_rss, total_rss = get_rss_data(rss_data)
    avail_df = create_resource_dataframe(avail_rss)
    total_df = create_resource_dataframe(total_rss)

    format_dataframe_for_display(avail_df)
    format_dataframe_for_display(total_df)
    return avail_df, total_df


if __name__ == "__main__":
    try:
        _date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        avail_df, total_df = process_rss()
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
    except Exception as e:
        print(f"Error generating report: {e}")
        traceback.print_exc()
    finally:
        input()
