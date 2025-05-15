import os
import sqlite3
from datetime import datetime

DATABASE_FILE_NAME = "installed_versions.db"


# Initialize the database and create the table if it doesn't exist
def initialize_db(data_dir):
    """Initialize the database and create the table if it doesn't exist."""  
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    DB_FILE = os.path.join(data_dir, DATABASE_FILE_NAME)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS installed_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            release TEXT NOT NULL,
            packageName TEXT NOT NULL,
            version TEXT NOT NULL,
            versionCode INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    return DB_FILE

# Insert a new record into the table
def insert_record(DB_FILE, repo, release, packageName, version, versionCode, date=None):
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO installed_versions (repo, release, packageName, version, versionCode, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (repo, release, packageName, version, versionCode, date))
    conn.commit()
    conn.close()

# Check if release exists in DB - based on repo and release values
def release_exist(DB_FILE, repo, release):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM installed_versions WHERE repo = ? AND release = ?', (repo, release))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Fetch all records from the table
def fetch_all_records(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM installed_versions')
    records = cursor.fetchall()
    conn.close()
    return records

# Get all records in string format
def get_all_records_string(DB_FILE):
    records = fetch_all_records()
    records_str = []
    for record in records:
        records_str.append(f"id: {record[0]}, repo: {record[1]}, rel: {record[2]}, pkgN: {record[3]}, ver: {record[4]}, verC: {record[5]}, date: {record[6]}")
    return '\n'.join(records_str)

# Get table information in string format
def get_table_columns(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(installed_versions)')
    columns = [column[1] for column in cursor.fetchall()]
    conn.close()
    return ', '.join(columns)

# Fetch records by package name
def fetch_records_by_package(DB_FILE, packageName):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM installed_versions WHERE packageName = ?', (packageName,))
    records = cursor.fetchall()
    conn.close()
    return records

# Delete a record by ID
def delete_record_by_id(DB_FILE, record_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM installed_versions WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()

# # Example usage
# if __name__ == "__main__":
#     initialize_db()
#     insert_record("repo1", "release1", "package1", "1.0.0", 100)
#     insert_record("repo2", "release2", "package2", "2.0.0", 200)
#     insert_record("repo3", "release3", "package3", "3.0.0", 300)
#     logger.info(fetch_all_records())
#     logger.info(fetch_records_by_package("package1"))
#     # delete_record_by_id(1)
#     # logger.info(fetch_all_records())
