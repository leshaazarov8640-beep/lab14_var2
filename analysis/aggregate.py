import polars as pl


def aggregate_weather(df: pl.DataFrame) -> pl.DataFrame:
    agg = df.group_by("city").agg([
        pl.col("temp").mean().alias("avg_temp"),
        pl.col("temp").min().alias("min_temp"),
        pl.col("temp").max().alias("max_temp"),
        pl.col("humidity").mean().alias("avg_humidity"),
        pl.col("pressure").mean().alias("avg_pressure"),
        pl.col("wind_speed").mean().alias("avg_wind_speed"),
        pl.count().alias("measurements"),
    ]).sort("avg_temp", descending=True)

    print("Aggregation by city:")
    print(agg)
    return agg
