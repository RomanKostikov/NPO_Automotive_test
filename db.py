import sqlite3


class DatabaseManager:
    def __init__(self, db_name="resources.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL,
                ram_free REAL,
                disk_free REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insert_record(self, cpu, ram_free, disk_free):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO records (cpu_usage, ram_free, disk_free)
            VALUES (?, ?, ?)
        """, (cpu, ram_free, disk_free))
        self.conn.commit()

    def fetch_all_records(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, cpu_usage, ram_free, disk_free, timestamp
            FROM records
        """)
        return cursor.fetchall()

    def close(self):
        self.conn.close()
