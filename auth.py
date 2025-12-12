# -*- coding: utf-8 -*-

class AuthManager:
    def __init__(self, database):
        self.db = database

    def register_user(self, username, password, full_name, group_name=""):
        existing = self.db.fetch_one("SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            return False, "Пользователь с таким логином уже существует"

        password_hash = self.db.hash_password(password)

        query = """
            INSERT INTO users (username, password_hash, full_name, group_name)
            VALUES (?, ?, ?, ?)
        """
        cursor = self.db.execute_query(query, (username, password_hash, full_name, group_name))

        if cursor and cursor.lastrowid:
            self._create_sample_project(cursor.lastrowid, full_name)
            return True, "Регистрация успешна"
        else:
            return False, "Ошибка при регистрации"

    def _create_sample_project(self, user_id, full_name):
        try:
            query = """
                INSERT INTO projects (name, description, creator_id)
                VALUES (?, ?, ?)
            """
            cursor = self.db.execute_query(
                query,
                ("Мой первый проект",
                 f"Добро пожаловать в систему, {full_name}! Это ваш первый проект.",
                 user_id)
            )

            if cursor and cursor.lastrowid:
                project_id = cursor.lastrowid
                self.db.execute_query(
                    "INSERT INTO project_members (project_id, user_id) VALUES (?, ?)",
                    (project_id, user_id)
                )

                self.db.execute_query('''
                    INSERT INTO tasks (title, description, status, project_id, creator_id, priority)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ("Изучить систему", "Ознакомиться с возможностями системы управления проектами",
                      "todo", project_id, user_id, "medium"))
        except Exception as e:
            print(f"Ошибка создания тестового проекта: {e}")

    def login(self, username, password):
        password_hash = self.db.hash_password(password)

        query = """
            SELECT id, username, full_name, group_name FROM users 
            WHERE username = ? AND password_hash = ?
        """
        user = self.db.fetch_one(query, (username, password_hash))

        if user:
            return True, dict(user)
        return False, None

    def get_user_by_id(self, user_id):
        query = "SELECT id, username, full_name, group_name FROM users WHERE id = ?"
        user = self.db.fetch_one(query, (user_id,))
        return dict(user) if user else None

    def get_user_by_username(self, username):
        query = "SELECT id, username, full_name, group_name FROM users WHERE username = ?"
        user = self.db.fetch_one(query, (username,))
        return dict(user) if user else None