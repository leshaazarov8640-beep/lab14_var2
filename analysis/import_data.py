import polars as pl
import json
import os
from pathlib import Path


def import_weather_data(filepath: str) -> pl.DataFrame:
    records = []
    filepath = os.path.join(os.path.dirname(__file__), "..", filepath)

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return pl.DataFrame()

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    if not records:
        print("No data found")
        return pl.DataFrame()

    df = pl.DataFrame(records)
    print(f"Loaded {len(df)} records from {filepath}")
    print(f"Columns: {df.columns}")
    print(f"Schema:\n{df.schema}")
    print(f"\nFirst 5 rows:\n{df.head()}")
    return df


if __name__ == "__main__":
    df = import_weather_data("data/weather_data.json")
    if df.height > 0:
        print(f"\nBasic statistics:\n{df.describe()}")
