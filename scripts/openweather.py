import click
import requests
import pandas as pd
from datetime import datetime, timedelta
from home_messages_db import HomeMessagesDB, Weather
from sqlalchemy.exc import SQLAlchemyError

@click.command()
@click.option('-d', '--dburl', required=True, help='SQLAlchemy database URL (e.g., sqlite:///smarthome.db)')
def openweather(dburl):
    """
    Fetch historical weather data from Open-Meteo API and insert into the database in bulk.

    Usage:
        openweather.py [OPTIONS]

    Output options:
        -d DBURL insert into the project database (DBURL is a SQLAlchemy database URL)
    """
    # Coordinates for Nordwijk, NL
    lat = 52.2387  # Latitude
    lon = 4.4425   # Longitude

    # Date range: 32 months from June 2022 to January 2025 (as per assignment context)
    start_date = datetime(2022, 6, 1)  # Start date
    end_date = datetime(2025, 1, 31)  # End date (covers 32 months)

    # Initialize database connection
    db = HomeMessagesDB(dburl)
    total_inserted = 0

    try:
        # Break the date range into 3-month chunks to avoid API overload
        current_start = start_date
        while current_start < end_date:
            current_end = min(current_start + timedelta(days=90), end_date)
            click.echo(f"Fetching weather data from {current_start.date()} to {current_end.date()}...")

            # Construct Open-Meteo API URL
            base_url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                'latitude': lat,
                'longitude': lon,
                'start_date': current_start.date().isoformat(),
                'end_date': current_end.date().isoformat(),
                'hourly': 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,surface_pressure',
                'timezone': 'UTC'
            }

            # Fetch data
            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                raise click.ClickException(f"Failed to fetch weather data: {response.status_code} - {response.text}")
            else:
                click.echo(f"API response: {response.status_code}")

            data = response.json()
            hourly = data.get('hourly', {})

            # Check if required fields are present
            required_fields = ['time', 'temperature_2m', 'relative_humidity_2m', 'precipitation', 'wind_speed_10m', 'surface_pressure']
            if not all(field in hourly for field in required_fields):
                raise click.ClickException(f"Missing required fields in API response: {hourly.keys()}")

            # Convert to DataFrame for easier processing
            df = pd.DataFrame({
                'time': hourly['time'],
                'temperature': hourly['temperature_2m'],
                'humidity': hourly['relative_humidity_2m'],
                'precipitation': hourly['precipitation'],
                'wind_speed': hourly['wind_speed_10m'],
                'pressure': hourly['surface_pressure']
            })

            # Convert time to epoch (Unix timestamp in seconds)
            df['epoch'] = pd.to_datetime(df['time'], utc=True).astype('int64') // 10**9

            # Convert wind speed from km/h to m/s (1 km/h = 1/3.6 m/s)
            df['wind_speed'] = df['wind_speed'] / 3.6

            # Prepare data for bulk insertion
            weather_data = [
                {
                    'epoch': row['epoch'],
                    'temperature': row['temperature'],
                    'humidity': row['humidity'],
                    'precipitation': row['precipitation'],
                    'wind_speed': row['wind_speed'],
                    'pressure': row['pressure']
                }
                for _, row in df.iterrows()
                if all(row[field] is not None for field in ['temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure'])
            ]

            # Bulk insert into database
            inserted = db.bulk_insert_weather(weather_data)
            total_inserted += inserted
            click.echo(f"Inserted {inserted} new weather records for {current_start.date()} to {current_end.date()}")

            # Move to the next chunk
            current_start = current_end + timedelta(days=1)

        click.echo(f"Total new weather records inserted: {total_inserted}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    openweather()