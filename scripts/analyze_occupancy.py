import click
from home_messages_db import HomeMessagesDB
import pandas as pd
from datetime import timedelta

@click.command()
@click.option('-d', '--dburl', required=True, help='SQLAlchemy database URL (e.g., sqlite:///smarthome.db)')
def analyze_occupancy(dburl):
    """Identify time intervals when nobody is at home based on low SmartThings activity."""
    db = HomeMessagesDB(dburl)

    try:
        # Fetch SmartThings data
        smartthings_data = db.query_smartthings()

        # Convert to DataFrame
        df = pd.DataFrame([(s.epoch, s.capability, s.attribute, s.value) for s in smartthings_data],
                         columns=['epoch', 'capability', 'attribute', 'value'])

        # Filter relevant capabilities (e.g., switch, motion)
        activity_df = df[df['capability'].isin(['switch', 'motionSensor'])]

        # Sort by epoch and calculate time gaps
        activity_df = activity_df.sort_values('epoch')
        activity_df['next_epoch'] = activity_df['epoch'].shift(-1)
        activity_df['gap'] = activity_df['next_epoch'] - activity_df['epoch']

        # Identify gaps longer than a threshold (e.g., 1 hour = 3600 seconds)
        threshold = 3600
        unoccupied_intervals = activity_df[activity_df['gap'] > threshold].copy()
        unoccupied_intervals['start_time'] = pd.to_datetime(unoccupied_intervals['epoch'], unit='s', utc=True)
        unoccupied_intervals['end_time'] = pd.to_datetime(unoccupied_intervals['next_epoch'], unit='s', utc=True)

        # Save results
        unoccupied_intervals[['start_time', 'end_time', 'gap']].to_csv('unoccupied_intervals.csv', index=False)
        click.echo("Unoccupied intervals saved to 'unoccupied_intervals.csv'")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    analyze_occupancy()