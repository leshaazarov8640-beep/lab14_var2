import polars as pl
import plotly.express as px
import plotly.graph_objects as go


def create_visualizations(df: pl.DataFrame) -> None:
    agg = df.group_by("city").agg([
        pl.col("temp").mean().alias("avg_temp"),
        pl.col("temp").min().alias("min_temp"),
        pl.col("temp").max().alias("max_temp"),
    ]).sort("avg_temp", descending=True)

    fig1 = px.bar(
        agg.to_pandas(),
        x="city",
        y="avg_temp",
        title="Average Temperature by City",
        labels={"avg_temp": "Temperature (°C)", "city": "City"},
        color="avg_temp",
        color_continuous_scale="RdYlBu_r",
    )
    fig1.write_html("docs/temperature_by_city.html")
    fig1.write_image("docs/temperature_by_city.png")
    print("Saved: temperature_by_city.html/png")

    pandas_df = df.to_pandas()
    fig2 = px.scatter(
        pandas_df,
        x="temp",
        y="humidity",
        color="city",
        title="Temperature vs Humidity",
        labels={"temp": "Temperature (°C)", "humidity": "Humidity (%)"},
        opacity=0.7,
    )
    fig2.write_html("docs/temp_vs_humidity.html")
    fig2.write_image("docs/temp_vs_humidity.png")
    print("Saved: temp_vs_humidity.html/png")

    weather_counts = df.group_by("weather_desc").agg([
        pl.count().alias("count")
    ]).sort("count", descending=True)

    fig3 = px.pie(
        weather_counts.to_pandas(),
        values="count",
        names="weather_desc",
        title="Weather Conditions Distribution",
    )
    fig3.write_html("docs/weather_conditions.html")
    fig3.write_image("docs/weather_conditions.png")
    print("Saved: weather_conditions.html/png")


def main():
    df = pl.read_parquet("data/weather_clean.parquet")
    create_visualizations(df)


if __name__ == "__main__":
    main()
