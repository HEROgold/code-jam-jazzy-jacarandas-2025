import random

import numpy as np
from pandas import DataFrame
from plotly.graph_objects import Candlestick, Figure, Pie, Scatter, Scatterpolar

from code_jam_jazzy_jacarandas_2025.settings import FetcherSettings, Settings


def create_candlestick_chart(df_ohlc: DataFrame) -> Figure:
    """Create candlestick chart from OHLC data."""
    fig = Figure(
        data=[
            Candlestick(
                x=df_ohlc["date"],
                open=df_ohlc["Open"],
                high=df_ohlc["High"],
                low=df_ohlc["Low"],
                close=df_ohlc["Close"],
            ),
        ],
    )

    fig.update_layout(
        title={
            "text": f"Daily Temperature OHLC (°C) in {FetcherSettings.country_name}",
            "x": 0.5,
        },
        xaxis_rangeslider_visible=True,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date",
            range=[df_ohlc["date"].iloc[-FetcherSettings.forecast_days], df_ohlc["date"].iloc[-1]],
        ),
        yaxis_title="Temperature (°C)",
        font={
            "family": Settings.font_family,
            "size": 14,
        },
    )

    return fig


def create_pie_chart(df_ohlc: DataFrame) -> Figure:
    """Create pie chart showing daily highest temperatures."""
    labels = df_ohlc["date"].dt.strftime("%b %d")
    values = df_ohlc["High"]

    fig_pie_all = Figure(
        data=[
            Pie(
                labels=labels,
                values=values,
                hovertemplate="%{label}<br>%{value:.2f}°C<extra></extra>",
            )
        ],
    )

    fig_pie_all.update_layout(
        title={
            "text": f"Daily Highest Temperatures in {FetcherSettings.country_name}",
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "family": Settings.font_family,
                "size": 24,
            },
        },
        font={
            "family": Settings.font_family,
            "size": 12,
        },
    )

    return fig_pie_all


def create_rain_radar_chart(hourly_dataframe: DataFrame) -> Figure:
    """Create a creative radar chart for precipitation data."""
    # Use real precipitation data from API
    hourly_dataframe["hour"] = hourly_dataframe["date"].dt.hour
    rain_by_hour = hourly_dataframe.groupby("hour")["precipitation"].mean().reset_index()

    # Create 24-hour labels
    hours = list(range(24))
    rain_values: list[float] = []

    for hour in hours:
        value = rain_by_hour[rain_by_hour["hour"] == hour]["precipitation"]
        rain_values.append(float(value.iloc[0]) if len(value) > 0 else 0.0)

    # Add first value at the end to close the radar chart
    rain_values.append(rain_values[0])
    hour_labels = [f"{h:02d}:00" for h in hours] + [f"{hours[0]:02d}:00"]

    fig_rain = Figure()

    # Add radar trace
    fig_rain.add_trace(
        Scatterpolar(
            r=rain_values,
            theta=hour_labels,
            fill="toself",
            fillcolor="rgba(54, 162, 235, 0.3)",
            line={"color": "rgba(54, 162, 235, 1)", "width": 3},
            marker={"size": 8, "color": "rgba(54, 162, 235, 1)"},
            name="Precipitation",
            hovertemplate="%{theta}<br>%{r:.2f} mm<extra></extra>",
        )
    )

    max_rain = max(rain_values) if rain_values else 1
    fig_rain.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, max_rain * 1.1] if max_rain > 0 else [0, 1],
                "tickfont": {"size": 10},
            },
            "angularaxis": {"tickfont": {"size": 12}, "rotation": 90, "direction": "clockwise"},
        },
        title={
            "text": f"24-Hour Precipitation Radar in {FetcherSettings.country_name}",
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "family": Settings.font_family,
                "size": 20,
            },
        },
        font={
            "family": Settings.font_family,
            "size": 12,
        },
        showlegend=False,
    )

    return fig_rain


def create_wind_spiral_chart(hourly_dataframe: DataFrame) -> Figure:
    """Create a creative wind speed chart organized by date coordinates."""
    # Use real wind speed data from API
    hourly_dataframe["day"] = hourly_dataframe["date"].dt.date
    daily_wind = hourly_dataframe.groupby("day")["wind_speed_10m"].mean().reset_index()

    if len(daily_wind) == 0:
        return Figure()

    # Setup the seed for random, ensuring reproducibility
    # Seed is made absolute as "np.random.default_rng" expects a positive value
    seed = int(abs(FetcherSettings.latitude + FetcherSettings.longitude))
    random.seed(seed)
    rng = np.random.default_rng(seed)

    # Create organized coordinates based on dates
    # X-axis represents day of forecast (0 to n)
    # Y-axis represents wind speed scaled
    # This creates a more organized visualization than the spiral
    daily_wind = daily_wind.sort_values("day").reset_index(drop=True)
    wind_speeds = daily_wind["wind_speed_10m"].tolist()
    x_coords = list(range(len(daily_wind)))  # Day index (0, 1, 2, ...)
    y_coords = list(random.choices(wind_speeds, k=len(daily_wind)))  # noqa: S311

    # Add random deviation of 25% to x and y coordinates for more natural data visualization
    x_deviation = rng.uniform(-0.25, 0.25, len(x_coords))  # 25% deviation
    y_deviation = rng.uniform(-0.25, 0.25, len(y_coords))  # 25% deviation

    # Apply deviation - multiply by original values to maintain scale
    x_coords = [x * (1 + dev) for x, dev in zip(x_coords, x_deviation, strict=False)]
    y_coords = [y * (1 + dev) for y, dev in zip(y_coords, y_deviation, strict=False)]

    # Create color scale based on wind speed
    colors = daily_wind["wind_speed_10m"].tolist()
    dates = [str(d) for d in daily_wind["day"]]

    # Create size based on wind speed for visual emphasis
    sizes = [max(8, min(20, speed * 1.5)) for speed in wind_speeds]

    fig_wind = Figure()

    # Add organized scatter plot
    fig_wind.add_trace(
        Scatter(
            x=x_coords,
            y=y_coords,
            mode="markers+lines",
            marker={
                "size": sizes,
                "color": colors,
                "colorscale": "Viridis",
                "showscale": True,
                "colorbar": {
                    "title": "Wind Speed (km/h)",
                },
                "line": {"width": 1, "color": "DarkSlateGrey"},
            },
            line={"width": 2, "color": "rgba(100, 100, 100, 0.5)"},
            text=dates,
            customdata=wind_speeds,
            hovertemplate="Date: %{text}<br>Wind Speed: %{customdata:.1f} km/h<br>Day: %{x}<extra></extra>",
            name="Wind Speed Journey",
        )
    )

    fig_wind.update_layout(
        title={
            "text": (f"Wind Speed Timeline in {FetcherSettings.country_name}<br><sub>X-axis: Days from start</sub>"),
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "family": Settings.font_family,
                "size": 18,
            },
        },
        xaxis={"showgrid": True, "zeroline": False, "title": "Days from Start"},
        font={
            "family": Settings.font_family,
            "size": 12,
        },
        showlegend=False,
        plot_bgcolor="rgba(245,245,245,0.8)",
    )

    return fig_wind
