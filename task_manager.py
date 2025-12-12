# -*- coding: utf-8 -*-

class TaskManager:

    def __init__(self, database):
        self.db = database

        self.statuses = {
            'todo': 'К выполнению',
            'in_progress': 'В процессе',
            'review': 'На проверке',
            'completed': 'Завершена'
        }

        self.priorities = {
            'low': 'Низкий',
            'medium': 'Средний',
            'high': 'Высокий'
        }

    def get_status_name(self, status_code):
        return self.statuses.get(status_code, 'Неизвестный статус')

    def get_priority_name(self, priority_code):
        return self.priorities.get(priority_code, 'Средний')

    def create_task(self, title, description, project_id, creator_id, deadline=None, priority='medium'):
        query = """
            INSERT INTO tasks (title, description, project_id, creator_id, deadline, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(
            query, (title, description, project_id, creator_id, deadline, priority)
        )

        if cursor and cursor.lastrowid:
            return True, cursor.lastrowid
        return False, None

    def get_project_tasks(self, project_id):
        query = """
            SELECT t.*, 
                   u_assignee.full_name as assignee_name,
                   u_creator.full_name as creator_name
            FROM tasks t
            LEFT JOIN users u_assignee ON t.assignee_id = u_assignee.id
            LEFT JOIN users u_creator ON t.creator_id = u_creator.id
            WHERE t.project_id = ?
            ORDER BY 
                CASE t.priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END,
                t.created_at DESC
        """
        tasks = self.db.fetch_all(query, (project_id,))
        return [dict(task) for task in tasks]

    def get_task_by_id(self, task_id):
        query = """
            SELECT t.*, 
                   u_assignee.full_name as assignee_name,
                   u_creator.full_name as creator_name
            FROM tasks t
            LEFT JOIN users u_assignee ON t.assignee_id = u_assignee.id
            LEFT JOIN users u_creator ON t.creator_id = u_creator.id
            WHERE t.id = ?
        """
        task = self.db.fetch_one(query, (task_id,))
        return dict(task) if task else None

    def get_user_tasks(self, user_id, project_id=None):
        query = """
            SELECT t.*, p.name as project_name
            FROM tasks t
            INNER JOIN projects p ON t.project_id = p.id
            WHERE t.assignee_id = ?
        """
        params = [user_id]

        if project_id:
            query += " AND t.project_id = ?"
            params.append(project_id)

        query += " ORDER BY t.deadline, t.priority"
        tasks = self.db.fetch_all(query, params)
        return [dict(task) for task in tasks]

    def assign_task(self, task_id, assignee_id):
        query = "UPDATE tasks SET assignee_id = ? WHERE id = ?"
        cursor = self.db.execute_query(query, (assignee_id, task_id))
        return cursor is not None and cursor.rowcount > 0

    def update_task_status(self, task_id, status):
        if status not in self.statuses:
            return False

        query = "UPDATE tasks SET status = ? WHERE id = ?"
        cursor = self.db.execute_query(query, (status, task_id))
        return cursor is not None and cursor.rowcount > 0

    def update_task_title(self, task_id, new_title):
        if not new_title:
            return False

        query = "UPDATE tasks SET title = ? WHERE id = ?"
        cursor = self.db.execute_query(query, (new_title, task_id))
        return cursor is not None and cursor.rowcount > 0

    def update_task_description(self, task_id, new_description):
        query = "UPDATE tasks SET description = ? WHERE id = ?"
        cursor = self.db.execute_query(query, (new_description, task_id))
        return cursor is not None and cursor.rowcount > 0

    def update_task_deadline(self, task_id, new_deadline):
        query = "UPDATE tasks SET deadline = ? WHERE id = ?"
        cursor = self.db.execute_query(query, (new_deadline, task_id))
        return cursor is not None and cursor.rowcount > 0

    def update_task_priority(self, task_id, new_priority):
        if new_priority not in self.priorities:
            return False

        query = "UPDATE tasks SET priority = ? WHERE id = ?"
        cursor = self.db.execute_query(query, (new_priority, task_id))
        return cursor is not None and cursor.rowcount > 0

    def delete_task(self, task_id):
        query = "DELETE FROM tasks WHERE id = ?"
        cursor = self.db.execute_query(query, (task_id,))
        return cursor is not None and cursor.rowcount > 0

    def get_task_statistics(self, project_id):
        query = """
            SELECT 
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_tasks,
                SUM(CASE WHEN status = 'review' THEN 1 ELSE 0 END) as review_tasks,
                SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) as todo_tasks
            FROM tasks 
            WHERE project_id = ?
        """
        stats = self.db.fetch_one(query, (project_id,))
        return dict(stats) if stats else None