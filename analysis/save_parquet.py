import polars as pl


def save_to_parquet(df: pl.DataFrame, filepath: str = "data/weather_clean.parquet") -> str:
    df.write_parquet(filepath, compression="zstd")
    print(f"Saved {df.height} records to {filepath}")
    return filepath
