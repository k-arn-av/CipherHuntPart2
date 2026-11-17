import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path):
        self.db_path = str(db_path)
        self._memory_connection = None
        self.initialize()

    def connect(self):
        if self.db_path== ":memory:":
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(":memory:")
                self._memory_connection.execute("PRAGMA foreign_keys = ON")
            return self._memory_connection

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def execute(self, sql, params=()):
        conn = self.connect()
        try:
            cursor= conn.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            if self.db_path!= ":memory:":
                conn.close()

    def initialize(self):
        if self.db_path!= ":memory:":
            Path(self.db_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

        conn= self.connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    current_points INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS clues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    clue_text TEXT NOT NULL,
                    key TEXT NOT NULL,
                    date_created TEXT NOT NULL,
                    is_solved INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """
            )
            conn.commit()
        finally:
            if self.db_path!= ":memory:":
                conn.close()

    def fetchone(self, sql, params=()):
        conn= self.connect()
        try:
            return conn.execute(sql, params).fetchone()
        finally:
            if self.db_path!= ":memory:":
                conn.close()

    def fetchall(self, sql, params=()):
        conn= self.connect()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            if self.db_path!= ":memory:":
                conn.close()