import duckdb
import time


def analyze_with_duckdb(parquet_path: str = "data/weather_clean.parquet"):
    conn = duckdb.connect()

    start = time.time()
    result = conn.execute("""
        SELECT
            city,
            AVG(temp) as avg_temp,
            MIN(temp) as min_temp,
            MAX(temp) as max_temp,
            AVG(humidity) as avg_humidity,
            AVG(wind_speed) as avg_wind,
            COUNT(*) as measurements
        FROM 'data/weather_clean.parquet'
        WHERE temp > -20 AND temp < 45
        GROUP BY city
        HAVING COUNT(*) > 1
        ORDER BY avg_temp DESC
    """).fetchdf()
    elapsed = time.time() - start

    print("DuckDB Analysis Results:")
    print(result.to_string(index=False))
    print(f"\nQuery executed in {elapsed:.3f}s")
    conn.close()
    return result


if __name__ == "__main__":
    analyze_with_duckdb()
