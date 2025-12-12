# -*- coding: utf-8 -*-

class ProjectManager:

    def __init__(self, database):
        self.db = database

    def create_project(self, name, description, creator_id):
        query = """
            INSERT INTO projects (name, description, creator_id)
            VALUES (?, ?, ?)
        """
        cursor = self.db.execute_query(query, (name, description, creator_id))

        if cursor and cursor.lastrowid:
            project_id = cursor.lastrowid
            self.add_member_to_project(project_id, creator_id, is_creator=True)
            return True, project_id
        return False, None

    def get_user_projects(self, user_id):
        query = """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM project_members WHERE project_id = p.id) as member_count
            FROM projects p
            INNER JOIN project_members pm ON p.id = pm.project_id
            WHERE pm.user_id = ?
            ORDER BY p.created_at DESC
        """
        projects = self.db.fetch_all(query, (user_id,))
        return [dict(project) for project in projects]

    def get_project_by_id(self, project_id):
        query = """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM project_members WHERE project_id = p.id) as member_count
            FROM projects p
            WHERE p.id = ?
        """
        project = self.db.fetch_one(query, (project_id,))
        return dict(project) if project else None

    def add_member_to_project(self, project_id, username_or_id, is_creator=False):
        if isinstance(username_or_id, str):
            user = self.db.fetch_one(
                "SELECT id FROM users WHERE username = ?",
                (username_or_id,)
            )
            if not user:
                return False, "Пользователь не найден"
            user_id = user['id']
        else:
            user_id = username_or_id

        project = self.get_project_by_id(project_id)
        if not project:
            return False, "Проект не найден"

        existing = self.db.fetch_one(
            "SELECT * FROM project_members WHERE project_id = ? AND user_id = ?",
            (project_id, user_id)
        )
        if existing:
            return False, "Пользователь уже является участником проекта"

        query = "INSERT INTO project_members (project_id, user_id) VALUES (?, ?)"
        cursor = self.db.execute_query(query, (project_id, user_id))

        if cursor and cursor.rowcount > 0:
            message = "Участник добавлен" if not is_creator else "Проект создан"
            return True, message
        return False, "Ошибка при добавлении участника"

    def get_project_members(self, project_id):
        query = """
            SELECT u.id, u.username, u.full_name, u.group_name
            FROM users u
            INNER JOIN project_members pm ON u.id = pm.user_id
            WHERE pm.project_id = ?
            ORDER BY u.full_name
        """
        members = self.db.fetch_all(query, (project_id,))
        return [dict(member) for member in members]

    def is_user_in_project(self, project_id, user_id):
        query = """
            SELECT * FROM project_members 
            WHERE project_id = ? AND user_id = ?
        """
        result = self.db.fetch_one(query, (project_id, user_id))
        return result is not None