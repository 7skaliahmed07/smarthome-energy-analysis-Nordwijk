import click
import sqlite3
import gzip
import os
import pandas as pd

# Assume a database connection helper
def get_db_connection(db_path='smarthome.db'):
    return sqlite3.connect(db_path)

# Create tables if they don't exist
def initialize_tables(conn):
    cursor = conn.cursor()
    # Create tables based on your existing structure (adjust column names as needed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS electricity_usage (
            epoch INTEGER PRIMARY KEY,
            t1_kwh REAL,
            t2_kwh REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gas_usage (
            epoch INTEGER PRIMARY KEY,
            gas_m3 REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            epoch INTEGER PRIMARY KEY,
            temperature REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS smartthings_messages (
            epoch INTEGER,
            device_id TEXT,
            capability TEXT,
            value TEXT,
            PRIMARY KEY (epoch, device_id, capability)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            name TEXT
        )
    ''')
    conn.commit()

# Command group for the tool
@click.group()
def cli():
    """Smart Home Database Manager

    A tool to manage the smart home database, supporting data insertion, querying,
    and database details for the Nordwijk project.
    """
    conn = get_db_connection()
    initialize_tables(conn)
    conn.close()

# Command to insert data
@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--compressed', is_flag=True, help='Handle the input file as a compressed .gz file.')
def insert(file_path, compressed):
    """Insert data into the smart home database from a file.

    FILE_PATH: Path to the data file (CSV or compressed .gz file). The file should
    have columns matching one of the tables (e.g., epoch, t1_kwh, t2_kwh for
    electricity_usage).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Handle compressed files if specified
        if compressed and file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt') as f:
                df = pd.read_csv(f)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise click.BadParameter('File must be a .csv or .gz file.')

        # Determine table based on columns (simplified logic)
        if {'epoch', 't1_kwh', 't2_kwh'}.issubset(df.columns):
            table = 'electricity_usage'
            cursor.executemany(
                f'INSERT OR REPLACE INTO {table} (epoch, t1_kwh, t2_kwh) VALUES (?, ?, ?)',
                df[['epoch', 't1_kwh', 't2_kwh']].values
            )
        elif {'epoch', 'gas_m3'}.issubset(df.columns):
            table = 'gas_usage'
            cursor.executemany(
                f'INSERT OR REPLACE INTO {table} (epoch, gas_m3) VALUES (?, ?)',
                df[['epoch', 'gas_m3']].values
            )
        elif {'epoch', 'temperature'}.issubset(df.columns):
            table = 'weather'
            cursor.executemany(
                f'INSERT OR REPLACE INTO {table} (epoch, temperature) VALUES (?, ?)',
                df[['epoch', 'temperature']].values
            )
        elif {'epoch', 'device_id', 'capability', 'value'}.issubset(df.columns):
            table = 'smartthings_messages'
            cursor.executemany(
                f'INSERT OR REPLACE INTO {table} (epoch, device_id, capability, value) VALUES (?, ?, ?, ?)',
                df[['epoch', 'device_id', 'capability', 'value']].values
            )
        elif {'device_id', 'name'}.issubset(df.columns):
            table = 'devices'
            cursor.executemany(
                f'INSERT OR REPLACE INTO {table} (device_id, name) VALUES (?, ?)',
                df[['device_id', 'name']].values
            )
        else:
            raise click.BadParameter('File columns do not match any known table structure.')

        conn.commit()
        click.echo(f"Data inserted successfully into {table} from {file_path}")
    except sqlite3.Error as e:
        click.echo(f"Database error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
    finally:
        conn.close()

# Command to count entries
@cli.command()
def count():
    """Display the number of entries currently in the database for each table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        tables = ['electricity_usage', 'gas_usage', 'weather', 'smartthings_messages', 'devices']
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            click.echo(f"Number of entries in {table}: {count}")
    except sqlite3.Error as e:
        click.echo(f"Database error: {e}", err=True)
    finally:
        conn.close()

# Command to list tables
@cli.command()
def list_tables():
    """List all tables in the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        click.echo("Tables in the database:")
        for table in tables:
            click.echo(f"  ---> {table}")
    except sqlite3.Error as e:
        click.echo(f"Database error: {e}", err=True)
    finally:
        conn.close()

# Command to show table schema
@cli.command()
@click.argument('table_name', type=str)
def schema(table_name):
    """Display the schema (column names and types) of a specified table.

    TABLE_NAME: Name of the table to inspect (e.g., electricity_usage).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        click.echo(f"Schema for table '{table_name}':")
        for col in columns:
            click.echo(f"  ---> {col[1]} ({col[2]})")
    except sqlite3.Error as e:
        click.echo(f"Database error: {e}", err=True)
    finally:
        conn.close()

if __name__ == '__main__':
    cli()