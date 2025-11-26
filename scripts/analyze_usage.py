import click
from home_messages_db import HomeMessagesDB
import pandas as pd
from datetime import datetime

@click.command()
@click.option('-d', '--dburl', required=True, help='SQLAlchemy database URL (e.g., sqlite:///smarthome.db)')
def analyze_usage(dburl):
    """Analyze the distribution of energy and gas usage over a day by calculating usage differences."""
    db = HomeMessagesDB(dburl)

    try:
        # Fetch data
        electricity_data = db.query_electricity()
        gas_data = db.query_gas()

        # Convert to DataFrame and sort by epoch
        electricity_df = pd.DataFrame([(e.epoch, e.t1_kwh, e.t2_kwh) for e in electricity_data],
                                    columns=['epoch', 't1_kwh', 't2_kwh']).sort_values('epoch')
        gas_df = pd.DataFrame([(g.epoch, g.gas_m3) for g in gas_data],
                             columns=['epoch', 'gas_m3']).sort_values('epoch')

        # Calculate differences (actual usage between consecutive readings)
        electricity_df['t1_kwh_diff'] = electricity_df['t1_kwh'].diff().fillna(0)
        electricity_df['t2_kwh_diff'] = electricity_df['t2_kwh'].diff().fillna(0)
        gas_df['gas_m3_diff'] = gas_df['gas_m3'].diff().fillna(0)

        # Remove negative differences (invalid data, possibly meter resets)
        electricity_df = electricity_df[(electricity_df['t1_kwh_diff'] >= 0) & (electricity_df['t2_kwh_diff'] >= 0)]
        gas_df = gas_df[gas_df['gas_m3_diff'] >= 0]

        # Convert epoch to datetime and extract hour
        electricity_df['datetime'] = pd.to_datetime(electricity_df['epoch'], unit='s', utc=True)
        electricity_df['hour'] = electricity_df['datetime'].dt.hour
        gas_df['datetime'] = pd.to_datetime(gas_df['epoch'], unit='s', utc=True)
        gas_df['hour'] = gas_df['datetime'].dt.hour

        # Aggregate by hour (mean usage per hour across all days)
        hourly_electricity = electricity_df.groupby('hour').agg({
            't1_kwh_diff': 'mean',
            't2_kwh_diff': 'mean'
        }).reset_index()
        hourly_gas = gas_df.groupby('hour').agg({
            'gas_m3_diff': 'mean'
        }).reset_index()

        # Merge results
        hourly_usage = pd.merge(hourly_electricity, hourly_gas, on='hour', how='outer')
        hourly_usage = hourly_usage.rename(columns={
            't1_kwh_diff': 't1_kwh',
            't2_kwh_diff': 't2_kwh',
            'gas_m3_diff': 'gas_m3'
        })

        # Fill NaN values with 0
        hourly_usage = hourly_usage.fillna(0)

        # Save to CSV for visualization
        hourly_usage.to_csv('hourly_usage.csv', index=False)
        click.echo("Hourly usage distribution (differences) saved to 'hourly_usage.csv'")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    analyze_usage()