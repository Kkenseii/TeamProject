# -*- coding: utf-8 -*-

import sqlite3
import hashlib
from datetime import datetime


class Database:

    def __init__(self, db_name="student_projects.db"):
        self.db_name = db_name
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def init_database(self):
        try:
            cursor = self.connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    group_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    creator_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES users (id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_members (
                    project_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (project_id, user_id),
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'todo',
                    project_id INTEGER NOT NULL,
                    creator_id INTEGER NOT NULL,
                    assignee_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deadline DATE,
                    priority TEXT DEFAULT 'medium',
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (creator_id) REFERENCES users (id),
                    FOREIGN KEY (assignee_id) REFERENCES users (id)
                )
            ''')

            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print(f"Ошибка инициализации БД: {e}")
            return False

    def execute_query(self, query, params=()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None

    def fetch_one(self, query, params=()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка получения данных: {e}")
            return None

    def fetch_all(self, query, params=()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения данных: {e}")
            return []

    def close(self):
        if self.connection:
            self.connection.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()