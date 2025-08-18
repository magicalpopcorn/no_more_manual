#!python
# -*- coding: utf-8 -*-

import json
import os
import sys
from datetime import datetime
from pprint import pprint

import pandas as pd

sys.path.insert(0, os.getcwd())

from src import const, rok_profile
from src.const import PROJECT_ROOT
from src.element import ResourceAmount, ResourceSet, TaxRate
from src.task import Report

profile = rok_profile.RokProfile()
chars = profile.chars

_date_str = datetime.now().strftime("%Y-%m-%d")
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

df = pd.DataFrame(rows)
# Optional: order columns explicitly
df = df[["name", "ch", "tax", "food", "wood", "stone", "gold"]]
for col in ["food", "wood", "stone", "gold"]:
    df[f"{col}_after_tax"] = df.apply(lambda row: row[col].after_tax(row["tax"]), axis=1)
totals = df[[f"{col}_after_tax" for col in ["food", "wood", "stone", "gold"]]].sum()
# Build the summary row
summary_row = {
    "name": "TOTAL (AFTER TAX)",
    "ch": "",
    "tax": "",
    "food": totals["food_after_tax"],
    "wood": totals["wood_after_tax"],
    "stone": totals["stone_after_tax"],
    "gold": totals["gold_after_tax"],
}

# Append row to df
df_with_total = df.drop(
    columns=["food_after_tax", "wood_after_tax", "stone_after_tax", "gold_after_tax"]
)
df_with_total = pd.concat([df_with_total, pd.DataFrame([summary_row])], ignore_index=True)

pprint(df_with_total)
# Save DataFrame with totals to CSV
output_path = PROJECT_ROOT / "tmp" / "record" / f"resources_after_tax_{_date_str}.csv"
df_with_total.to_csv(output_path, index=False, encoding="utf-8")

print(f"Saved to {output_path}")
