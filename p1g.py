import click
import pandas as pd
from home_messages_db import HomeMessagesDB, GasUsage
from sqlalchemy.exc import SQLAlchemyError

@click.command()
@click.option('-d', '--dburl', required=True, help='SQLAlchemy database URL (e.g., sqlite:///smarthome.db)')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def p1g(dburl, files):
    """
    Insert gas usage data from P1g CSV files into the database in bulk.

    Usage:
        p1g.py [OPTIONS] P1g-2023-01-01-2023-01-10.csv [P1g-*.csv...]

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

            # Check for required columns
            if 'time' not in df.columns or 'Total gas used' not in df.columns:
                raise click.UsageError(f"Missing required columns in {file}. Expected 'time' and 'Total gas used'")

            # Rename column to match database schema
            df = df.rename(columns={'Total gas used': 'gas_m3'})

            # Convert time (YYYY-MM-DD HH:MM) to UTC datetime string (YYYY-MM-DD HH:MM:SS)
            df['epoch'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M', utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Ensure required columns after renaming
            required_columns = ['epoch', 'gas_m3']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise click.UsageError(f"Missing columns in {file} after processing: {missing}")

            # Remove duplicates within the file based on epoch
            df = df.drop_duplicates(subset=['epoch'])

            # Check for existing epochs to avoid duplicates
            existing_epochs = {row.epoch for row in db.session.query(GasUsage.epoch).all()}

            # Filter out rows with existing epochs
            new_rows = [
                {'epoch': row['epoch'], 'gas_m3': row['gas_m3']}
                for _, row in df.iterrows()
                if row['epoch'] not in existing_epochs
            ]

            # Bulk insert new rows
            if new_rows:
                try:
                    db.session.bulk_insert_mappings(GasUsage, new_rows)
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
    p1g()