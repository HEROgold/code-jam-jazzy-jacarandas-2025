# The Forecast Strikes Back

## What is this?

This is the `Jazzy Jacaranda's` submission for the 2025 Python Discord Summer Code Jam, with the theme of "wrong tool for the job."

## Features

- Temperature viewed as an OHLC chart
- Highest daily temperature viewed as a pie chart

## User Guide

The webserver will run on `http://localhost:3000`

### UV

Run in your terminal:

```bash
uv sync
uv run reflex run
```

### Poetry

```bash
poetry install
poetry run reflex run
```

### Docker

```bash
# pull the image
docker pull doodleheimer/jazzy_jacarandas
# run the container
docker run -it --rm -p 3000:3000 -p 8000:8000 doodleheimer/jazzy_jacarandas
```

From Docker Desktop make sure to put ports 3000 and 8000 in the optional settings.

## The Jazzy Jacarandas Team

| Avatar                                                     | Name                                            |
| ---------------------------------------------------------- | ------------------------------------------------|
| <img src="https://github.com/HEROgold.png" width="50">     | [Hero](https://github.com/HEROgold)             |
| <img src="https://github.com/kkiyomi.png" width="50">      | [KKiyomi](https://github.com/kkiyomi)           |
| <img src="https://github.com/artahadhahd.png" width="50">  | [Doodleheimer](https://github.com/artahadhahd)  |
| <img src="https://github.com/bananadado.png" width="50">   | [Bananadado](https://github.com/bananadado)     |
| <img src="https://github.com/AndreBinbow.png" width="50">  | [Andre Binbow](https://github.com/AndreBinbow)  |
