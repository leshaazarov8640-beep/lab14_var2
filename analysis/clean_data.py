import polars as pl


def clean_weather_data(df: pl.DataFrame) -> pl.DataFrame:
    initial_count = df.height
    print(f"Initial records: {initial_count}")

    df = df.unique(subset=["city", "timestamp"])

    df = df.drop_nulls()

    df = df.filter(
        (pl.col("temp") > -50) & (pl.col("temp") < 60)
    )

    df = df.with_columns([
        pl.col("timestamp").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.f%z", strict=False)
        .cast(pl.Datetime),
        pl.col("temp").cast(pl.Float64),
        pl.col("feels_like").cast(pl.Float64),
        pl.col("humidity").cast(pl.Int64),
        pl.col("pressure").cast(pl.Int64),
        pl.col("wind_speed").cast(pl.Float64),
    ])

    cleaned_count = df.height
    removed = initial_count - cleaned_count
    print(f"Removed {removed} records")
    print(f"Cleaned records: {cleaned_count}")

    print(f"\nCleaned data summary:\n{df.describe()}")
    return df
