import click
import pandas as pd
from home_messages_db import HomeMessagesDB, Device, SmartThingsMessage
from sqlalchemy.exc import SQLAlchemyError

@click.command()
@click.option('-d', '--dburl', required=True, help='SQLAlchemy database URL (e.g., sqlite:///smarthome.db)')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def smartthings(dburl, files):
    """
    Insert SmartThings data into the database in bulk.

    Usage:
        smartthings.py [OPTIONS] smartthingsLog.1.tsv [smartthingsLog.2.tsv...]

    Output options:
        -d DBURL insert into the project database (DBURL is a SQLAlchemy database URL)
    """
    if not files:
        raise click.UsageError("At least one input file must be provided.")

    db = HomeMessagesDB(dburl)
    try:
        for file in files:
            click.echo(f"Processing {file}...")
            # Read TSV file
            df = pd.read_csv(file, sep='\t')

            # Ensure required columns
            required_columns = ['loc', 'level', 'name', 'epoch', 'capability', 'attribute', 'value', 'unit']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise click.UsageError(f"Missing columns in {file}: {missing}")

            # Remove duplicates within the file
            df = df.drop_duplicates(subset=['name', 'epoch', 'capability', 'attribute'])

            # Insert or get devices
            devices = df[['name', 'loc', 'level']].drop_duplicates()
            device_map = {}
            for _, device in devices.iterrows():
                device_id = db.insert_device(device['name'], device['loc'], device['level'])
                device_map[device['name']] = device_id

            # Prepare messages with device_id
            messages = df.merge(
                pd.Series(device_map, name='device_id'),
                left_on='name',
                right_index=True
            )

            # Check for existing messages to avoid duplicates
            existing = db.session.query(
                SmartThingsMessage.device_id,
                SmartThingsMessage.epoch,
                SmartThingsMessage.capability,
                SmartThingsMessage.attribute
            ).all()
            existing_set = set((row.device_id, row.epoch, row.capability, row.attribute) for row in existing)

            # Filter out duplicates
            new_messages = [
                {
                    'device_id': row['device_id'],
                    'epoch': row['epoch'],
                    'capability': row['capability'],
                    'attribute': row['attribute'],
                    'value': str(row['value']),
                    'unit': str(row['unit'])
                }
                for _, row in messages.iterrows()
                if (row['device_id'], row['epoch'], row['capability'], row['attribute']) not in existing_set
            ]

            # Bulk insert new messages
            if new_messages:
                try:
                    db.session.bulk_insert_mappings(SmartThingsMessage, new_messages)
                    db.session.commit()
                    click.echo(f"Inserted {len(new_messages)} new rows from {file}.")
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
        click.echo(f"Error parsing TSV file: {e}", err=True)
        raise
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    smartthings()