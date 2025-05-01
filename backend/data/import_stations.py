#!/usr/bin/env python3
"""
Script to import stations from stations_coded.csv into the database
"""
import csv
import os
from pathlib import Path
from sqlmodel import delete

from api.database.models import Station
from api.database.connection import get_session


def clean_value(value):
    """Clean values from CSV file."""
    if value == "\\N" or value == "NULL" or value == "":
        return None
    return value


def import_stations():
    """Import stations from CSV file to database."""
    csv_file = os.path.join(Path(__file__).parent, "stations.csv")

    print(f"Importing stations from {csv_file}...")

    # Get a session from the connection module
    session = next(get_session())

    try:
        # First, let's clear any existing stations to avoid duplicates
        session.exec(delete(Station))
        session.commit()

        # Now read the CSV file and import stations
        with open(csv_file, "r", newline="") as f:
            reader = csv.DictReader(f)

            # Track progress
            total_stations = 0
            batch_size = 100
            batch = []

            for row in reader:
                # Create a Station object without specifying the id field
                station = Station(
                    name=row["name"].strip('"'),
                    longname=clean_value(row["longname"].strip('"')),
                    alpha=clean_value(row["alpha"].strip('"')),
                    code=row["code"].strip('"'),
                    code_two=clean_value(row["code_two"].strip('"')),
                    my_train_code=clean_value(row["my_train_code"].strip('"')),
                    anglia_code=clean_value(row["anglia_code"].strip('"')),
                    national_rail_code=clean_value(
                        row["national_rail_code"].strip('"')
                    ),
                )

                batch.append(station)
                total_stations += 1

                # Commit in batches to improve performance
                if len(batch) >= batch_size:
                    session.add_all(batch)
                    session.commit()
                    batch = []

            # Add any remaining stations
            if batch:
                session.add_all(batch)
                session.commit()

        print(f"Successfully imported {total_stations} stations!")

    finally:
        # Always close the session when done
        session.close()


if __name__ == "__main__":
    import_stations()
