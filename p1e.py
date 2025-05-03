import click
import pandas as pd
from home_messages_db import HomeMessagesDB, ElectricityUsage
from sqlalchemy.exc import SQLAlchemyError

@click.command()
@click.option('-d', '--dburl', required=True, help='SQLAlchemy database URL (e.g., sqlite:///smarthome.db)')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def p1e(dburl, files):
    """
    Insert electricity usage data from P1e CSV files into the database in bulk.

    Usage:
        p1e.py [OPTIONS] P1e-2022-12-01-2023-01-10.csv [P1e-*.csv...]

    Output options:
        -d DBURL insert into the project database (DBURL is a SQLAlchemy database URL)
    """
    if not files:
        raise click.UsageError("At least one input file must be provided.")

    db = HomeMessagesDB(dburl)
    try:
        for file in files:
            click.echo(f"Processing {file}...")
            # Read CSV file
            df = pd.read_csv(file)

            # Check for time column
            if 'time' not in df.columns:
                raise click.UsageError(f"Missing 'time' column in {file}")

            # Determine column names for t1_kwh and t2_kwh
            if 'Import T1 kWh' in df.columns and 'Import T2 kWh' in df.columns:
                df = df.rename(columns={
                    'Import T1 kWh': 't1_kwh',
                    'Import T2 kWh': 't2_kwh'
                })
            elif 'Electricity imported T1' in df.columns and 'Electricity imported T2' in df.columns:
                df = df.rename(columns={
                    'Electricity imported T1': 't1_kwh',
                    'Electricity imported T2': 't2_kwh'
                })
            else:
                raise click.UsageError(f"Missing electricity import columns in {file}. Expected 'Import T1 kWh'/'Import T2 kWh' or 'Electricity imported T1'/'Electricity imported T2'")

            # Convert time to UTC datetime string (YYYY-MM-DD HH:MM:SS)
            df['epoch'] = pd.to_datetime(df['time'], utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Ensure required columns after renaming
            required_columns = ['epoch', 't1_kwh', 't2_kwh']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise click.UsageError(f"Missing columns in {file} after processing: {missing}")

            # Remove duplicates within the file based on epoch
            df = df.drop_duplicates(subset=['epoch'])

            # Check for existing epochs to avoid duplicates
            existing_epochs = {row.epoch for row in db.session.query(ElectricityUsage.epoch).all()}

            # Filter out rows with existing epochs
            new_rows = [
                {'epoch': row['epoch'], 't1_kwh': row['t1_kwh'], 't2_kwh': row['t2_kwh']}
                for _, row in df.iterrows()
                if row['epoch'] not in existing_epochs
            ]

            # Bulk insert new rows
            if new_rows:
                try:
                    db.session.bulk_insert_mappings(ElectricityUsage, new_rows)
                    db.session.commit()
                    click.echo(f"Inserted {len(new_rows)} new rows from {file}.")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    click.echo(f"Database error (possible duplicate): {e}", err=True)
                    raise
            else:
                click.echo(f"No new rows to insert from {file} (all duplicates).")

            click.echo(f"Finished processing {file}. Total rows processed: {len(df)}")
    except SQLAlchemyError as e:
        db.session.rollback()
        click.echo(f"Database error: {e}", err=True)
        raise
    except pd.errors.ParserError as e:
        click.echo(f"Error parsing CSV file: {e}", err=True)
        raise
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    p1e()