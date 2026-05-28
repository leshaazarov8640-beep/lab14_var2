from import_data import import_weather_data
from clean_data import clean_weather_data
from aggregate import aggregate_weather
from save_parquet import save_to_parquet
from duckdb_analysis import analyze_with_duckdb
from visualize import create_visualizations
import polars as pl


def main():
    print("=" * 60)
    print("WEATHER DATA PIPELINE")
    print("=" * 60)

    print("\n[1/6] Importing data...")
    df = import_weather_data("data/weather_data.json")
    if df.height == 0:
        print("No data to process. Run the Go collector first.")
        return

    print("\n[2/6] Cleaning data...")
    df = clean_weather_data(df)

    print("\n[3/6] Aggregating data...")
    agg = aggregate_weather(df)

    print("\n[4/6] Saving to Parquet...")
    parquet_path = save_to_parquet(df)

    print("\n[5/6] DuckDB analysis...")
    analyze_with_duckdb()

    print("\n[6/6] Creating visualizations...")
    create_visualizations(df)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
