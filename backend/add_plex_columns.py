"""
Migration script to add Plex columns to the releases table.
Run this once to update your existing database.
"""
import sqlite3
import sys
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "releasedrop.db"

def add_plex_columns():
    """Add Plex-related columns to the releases table."""

    if not DB_PATH.exists():
        print(f"Database not found at: {DB_PATH}")
        print("   Make sure you're running this from the backend directory.")
        sys.exit(1)

    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(releases)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    columns_to_add = [
        ("in_plex", "BOOLEAN DEFAULT 0"),
        ("plex_match_type", "VARCHAR"),
        ("plex_match_confidence", "FLOAT"),
        ("plex_album_id", "VARCHAR"),
        ("plex_available_tracks", "JSON"),
        ("plex_missing_tracks", "JSON"),
    ]

    added_count = 0

    for column_name, column_type in columns_to_add:
        if column_name in existing_columns:
            print(f"⏭️  Column '{column_name}' already exists, skipping...")
        else:
            try:
                print(f"Adding column '{column_name}'...")
                cursor.execute(f"ALTER TABLE releases ADD COLUMN {column_name} {column_type}")
                added_count += 1
            except sqlite3.Error as e:
                print(f"Error adding column '{column_name}': {e}")
                conn.rollback()
                conn.close()
                sys.exit(1)

    conn.commit()
    conn.close()

    print(f"\nMigration complete! Added {added_count} new column(s).")
    if added_count == 0:
        print("   All Plex columns were already present.")
    else:
        print("   Your database is now ready for Plex integration!")

if __name__ == "__main__":
    add_plex_columns()
