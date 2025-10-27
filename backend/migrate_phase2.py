"""
Database migration script for Phase 2.
Adds new columns for Jellyfin integration and track information.
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings

def migrate():
    """Add Phase 2 columns to existing database."""
    settings = get_settings()
    db_path = settings.database_url.replace('sqlite:///', '')

    print(f"Migrating database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(releases)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    print(f"Existing columns: {existing_columns}")

    # Define new columns to add
    new_columns = {
        'jellyfin_match_type': 'TEXT',
        'jellyfin_match_confidence': 'REAL',
        'jellyfin_album_id': 'TEXT',
        'tracks': 'TEXT',  # JSON stored as TEXT in SQLite
        'available_tracks': 'TEXT',  # JSON stored as TEXT
        'missing_tracks': 'TEXT',  # JSON stored as TEXT
    }

    # Add missing columns
    added_count = 0
    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            try:
                sql = f'ALTER TABLE releases ADD COLUMN {column_name} {column_type}'
                cursor.execute(sql)
                print(f"Added column: {column_name}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"Column {column_name} may already exist: {e}")

    conn.commit()
    conn.close()

    if added_count > 0:
        print(f"\nMigration complete! Added {added_count} new columns.")
    else:
        print("\nNo migration needed - all columns already exist.")

if __name__ == "__main__":
    migrate()
