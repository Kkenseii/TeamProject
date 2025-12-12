#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from database import Database
from auth import AuthManager
from project_manager import ProjectManager
from task_manager import TaskManager


class StudentProjectCoordinator:

    def __init__(self):
        self.db = Database()
        self.auth = AuthManager(self.db)
        self.project_manager = ProjectManager(self.db)
        self.task_manager = TaskManager(self.db)
        self.current_user = None
        self.current_project = None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        print("=" * 60)
        print("СТУДЕНЧЕСКИЙ КООРДИНАТОР ПРОЕКТОВ".center(60))
        print("=" * 60)
        if self.current_user:
            print(f"Пользователь: {self.current_user['username']}")
            if self.current_project:
                print(f"Проект: {self.current_project['name']}")
        print("-" * 60)

    def main_menu(self):
        while True:
            self.clear_screen()
            self.display_header()

            if not self.current_user:
                print("1. Регистрация")
                print("2. Вход в систему")
                print("0. Выход")
            elif not self.current_project:
                print("1. Мои проекты")
                print("2. Создать новый проект")
                print("3. Выйти из аккаунта")
                print("0. Выход")
            else:
                print("1. Задачи проекта")
                print("2. Создать задачу")
                print("3. Участники проекта")
                print("4. Сменить проект")
                print("5. Выйти из аккаунта")
                print("0. Выход")

            print("-" * 60)
            choice = input("Выберите действие: ")

            if not self.current_user:
                if choice == "1":
                    self.register_user()
                elif choice == "2":
                    self.login_user()
                elif choice == "0":
                    print("Выход из приложения...")
                    break
                else:
                    self.show_error("Неверный выбор")

            elif not self.current_project:
                if choice == "1":
                    self.show_user_projects()
                elif choice == "2":
                    self.create_project()
                elif choice == "3":
                    self.logout_user()
                elif choice == "0":
                    print("Выход из приложения...")
                    break
                else:
                    self.show_error("Неверный выбор")

            else:
                if choice == "1":
                    self.show_project_tasks()
                elif choice == "2":
                    self.create_task()
                elif choice == "3":
                    self.show_project_members()
                elif choice == "4":
                    self.current_project = None
                elif choice == "5":
                    self.logout_user()
                elif choice == "0":
                    print("Выход из приложения...")
                    break
                else:
                    self.show_error("Неверный выбор")

            if choice != "0":
                input("\nНажмите Enter для продолжения...")

    def register_user(self):
        self.clear_screen()
        print("РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ")
        print("-" * 40)

        username = input("Логин: ").strip()
        password = input("Пароль: ").strip()
        full_name = input("ФИО: ").strip()
        group = input("Учебная группа: ").strip()

        if not username or not password or not full_name:
            self.show_error("Все поля обязательны для заполнения")
            return

        success, message = self.auth.register_user(username, password, full_name, group)
        if success:
            print(f"\n✓ {message}")
            success, user = self.auth.login(username, password)
            if success:
                self.current_user = user
                print(f"Добро пожаловать, {user['full_name']}!")
        else:
            self.show_error(message)

    def login_user(self):
        self.clear_screen()
        print("ВХОД В СИСТЕМУ")
        print("-" * 40)

        username = input("Логин: ").strip()
        password = input("Пароль: ").strip()

        success, user = self.auth.login(username, password)
        if success:
            self.current_user = user
            print(f"\n✓ Успешный вход!")
            print(f"Добро пожаловать, {user['full_name']}!")
        else:
            self.show_error("Неверный логин или пароль")

    def logout_user(self):
        self.current_user = None
        self.current_project = None
        print("Вы вышли из системы.")

    def show_user_projects(self):
        self.clear_screen()
        print("МОИ ПРОЕКТЫ")
        print("-" * 60)

        projects = self.project_manager.get_user_projects(self.current_user['id'])

        if not projects:
            print("У вас нет проектов.")
            return

        for i, project in enumerate(projects, 1):
            print(f"{i}. {project['name']}")
            print(f"   Описание: {project['description']}")
            print(f"   Дата создания: {project['created_at']}")
            print(f"   Участников: {project['member_count']}")
            print()

        print("-" * 60)
        print("0. Назад")

        choice = input("\nВыберите проект для открытия (номер): ")
        if choice == "0":
            return

        try:
            project_index = int(choice) - 1
            if 0 <= project_index < len(projects):
                self.current_project = projects[project_index]
                print(f"Проект '{self.current_project['name']}' открыт.")
            else:
                self.show_error("Неверный номер проекта")
        except ValueError:
            self.show_error("Введите число")

    def create_project(self):
        self.clear_screen()
        print("СОЗДАНИЕ НОВОГО ПРОЕКТА")
        print("-" * 40)

        name = input("Название проекта: ").strip()
        description = input("Описание проекта: ").strip()

        if not name:
            self.show_error("Название проекта обязательно")
            return

        success, project_id = self.project_manager.create_project(
            name, description, self.current_user['id']
        )

        if success:
            print(f"\n✓ Проект '{name}' создан!")
            project = self.project_manager.get_project_by_id(project_id)
            if project:
                self.current_project = project
        else:
            self.show_error("Ошибка при создании проекта")

    def show_project_tasks(self):
        self.clear_screen()
        print(f"ЗАДАЧИ ПРОЕКТА: {self.current_project['name']}")
        print("-" * 60)

        tasks = self.task_manager.get_project_tasks(self.current_project['id'])

        if not tasks:
            print("В проекте пока нет задач.")
        else:
            for i, task in enumerate(tasks, 1):
                status_icon = "✓" if task['status'] == 'completed' else "○"
                print(f"{i}. [{status_icon}] {task['title']}")
                print(f"   Описание: {task['description']}")
                print(f"   Статус: {self.task_manager.get_status_name(task['status'])}")
                print(f"   Исполнитель: {task['assignee_name'] or 'Не назначен'}")
                print(f"   Срок: {task['deadline'] or 'Не установлен'}")
                print(f"   Приоритет: {task['priority']}")
                print()

        print("-" * 60)
        print("1. Создать задачу")
        print("2. Изменить статус задачи")
        print("3. Назначить исполнителя")
        print("4. Редактировать задачу")
        print("0. Назад")

        choice = input("\nВыберите действие: ")

        if choice == "1":
            self.create_task()
        elif choice == "2":
            self.change_task_status(tasks)
        elif choice == "3":
            self.assign_task_to_user(tasks)
        elif choice == "4":
            self.edit_task(tasks)

    def create_task(self):
        self.clear_screen()
        print("СОЗДАНИЕ НОВОЙ ЗАДАЧИ")
        print("-" * 40)

        title = input("Название задачи: ").strip()
        description = input("Описание задачи: ").strip()
        deadline = input("Срок выполнения (ГГГГ-ММ-ДД): ").strip()

        print("\nПриоритет:")
        print("1. Низкий")
        print("2. Средний")
        print("3. Высокий")
        priority_choice = input("Выберите приоритет (1-3): ")

        priorities = {1: 'low', 2: 'medium', 3: 'high'}
        priority = priorities.get(int(priority_choice), 'medium') if priority_choice.isdigit() else 'medium'

        if not title:
            self.show_error("Название задачи обязательно")
            return

        success, task_id = self.task_manager.create_task(
            title=title,
            description=description,
            project_id=self.current_project['id'],
            creator_id=self.current_user['id'],
            deadline=deadline if deadline else None,
            priority=priority
        )

        if success:
            print(f"\n✓ Задача '{title}' создана!")

            assign_now = input("Назначить исполнителя сейчас? (y/n): ").lower()
            if assign_now == 'y':
                self.assign_task_immediately(task_id)
        else:
            self.show_error("Ошибка при создании задачи")

    def assign_task_immediately(self, task_id):
        members = self.project_manager.get_project_members(self.current_project['id'])

        if not members:
            print("В проекте нет других участников.")
            return

        print("\nДоступные участники:")
        for i, member in enumerate(members, 1):
            print(f"{i}. {member['full_name']} ({member['username']})")

        choice = input("\nВыберите исполнителя (номер) или 0 для отмены: ")
        if choice == "0":
            return

        try:
            member_index = int(choice) - 1
            if 0 <= member_index < len(members):
                assignee_id = members[member_index]['id']
                success = self.task_manager.assign_task(task_id, assignee_id)
                if success:
                    print(f"✓ Задача назначена {members[member_index]['full_name']}")
                else:
                    self.show_error("Ошибка при назначении задачи")
            else:
                self.show_error("Неверный номер участника")
        except ValueError:
            self.show_error("Введите число")

    def change_task_status(self, tasks):
        if not tasks:
            self.show_error("Нет задач для изменения")
            return

        print("\nИЗМЕНЕНИЕ СТАТУСА ЗАДАЧИ")
        print("-" * 40)

        task_num = input("Введите номер задачи для изменения статуса: ")

        try:
            task_index = int(task_num) - 1
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]

                print(f"\nТекущий статус: {self.task_manager.get_status_name(task['status'])}")
                print("\nДоступные статусы:")
                print("1. К выполнению")
                print("2. В процессе")
                print("3. На проверке")
                print("4. Завершена")

                status_choice = input("\nВыберите новый статус (1-4): ")
                status_map = {'1': 'todo', '2': 'in_progress', '3': 'review', '4': 'completed'}

                if status_choice in status_map:
                    new_status = status_map[status_choice]
                    success = self.task_manager.update_task_status(task['id'], new_status)
                    if success:
                        print(f"✓ Статус задачи изменен на: {self.task_manager.get_status_name(new_status)}")
                    else:
                        self.show_error("Ошибка при изменении статуса")
                else:
                    self.show_error("Неверный выбор статуса")
            else:
                self.show_error("Неверный номер задачи")
        except ValueError:
            self.show_error("Введите число")

    def assign_task_to_user(self, tasks):
        if not tasks:
            self.show_error("Нет задач для назначения")
            return

        print("\nНАЗНАЧЕНИЕ ИСПОЛНИТЕЛЯ")
        print("-" * 40)

        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['title']} - Исполнитель: {task['assignee_name'] or 'Не назначен'}")

        task_num = input("\nВведите номер задачи для назначения: ")

        try:
            task_index = int(task_num) - 1
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]
                members = self.project_manager.get_project_members(self.current_project['id'])

                print(f"\nЗадача: {task['title']}")
                print(f"Текущий исполнитель: {task['assignee_name'] or 'Не назначен'}")

                available_members = [m for m in members if m['id'] != task.get('assignee_id')]

                if available_members:
                    print("\nДоступные участники:")
                    for i, member in enumerate(available_members, 1):
                        print(f"{i}. {member['full_name']} ({member['username']})")

                    print("0. Снять назначение" if task['assignee_id'] else "0. Назад")

                    member_choice = input("\nВыберите исполнителя (номер): ")

                    if member_choice == "0":
                        if task['assignee_id']:
                            success = self.task_manager.assign_task(task['id'], None)
                            if success:
                                print("✓ Исполнитель снят с задачи")
                            else:
                                self.show_error("Ошибка при снятии исполнителя")
                        return
                    elif member_choice.isdigit():
                        member_index = int(member_choice) - 1
                        if 0 <= member_index < len(available_members):
                            assignee_id = available_members[member_index]['id']
                            success = self.task_manager.assign_task(task['id'], assignee_id)
                            if success:
                                print(f"✓ Задача назначена {available_members[member_index]['full_name']}")
                            else:
                                self.show_error("Ошибка при назначении задачи")
                        else:
                            self.show_error("Неверный номер участника")
                    else:
                        self.show_error("Введите число")
                else:
                    print("Нет доступных участников для назначения.")
            else:
                self.show_error("Неверный номер задачи")
        except ValueError:
            self.show_error("Введите число")

    def edit_task(self, tasks):
        if not tasks:
            self.show_error("Нет задач для редактирования")
            return

        print("\nРЕДАКТИРОВАНИЕ ЗАДАЧИ")
        print("-" * 40)

        task_num = input("Введите номер задачи для редактирования: ")

        try:
            task_index = int(task_num) - 1
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]

                print(f"\nРедактирование задачи: {task['title']}")
                print("-" * 40)

                print("1. Изменить название")
                print("2. Изменить описание")
                print("3. Изменить срок")
                print("4. Изменить приоритет")
                print("0. Назад")

                edit_choice = input("\nВыберите что редактировать: ")

                if edit_choice == "1":
                    new_title = input("Новое название: ").strip()
                    if new_title:
                        self.task_manager.update_task_title(task['id'], new_title)
                        print("✓ Название обновлено")
                    else:
                        self.show_error("Название не может быть пустым")

                elif edit_choice == "2":
                    new_description = input("Новое описание: ").strip()
                    self.task_manager.update_task_description(task['id'], new_description)
                    print("✓ Описание обновлено")

                elif edit_choice == "3":
                    new_deadline = input("Новый срок (ГГГГ-ММ-ДД): ").strip()
                    self.task_manager.update_task_deadline(task['id'], new_deadline if new_deadline else None)
                    print("✓ Срок обновлен")

                elif edit_choice == "4":
                    print("\nПриоритет:")
                    print("1. Низкий")
                    print("2. Средний")
                    print("3. Высокий")
                    priority_choice = input("Выберите приоритет (1-3): ")

                    if priority_choice in ['1', '2', '3']:
                        priority_map = {'1': 'low', '2': 'medium', '3': 'high'}
                        self.task_manager.update_task_priority(task['id'], priority_map[priority_choice])
                        print("✓ Приоритет обновлен")
                    else:
                        self.show_error("Неверный выбор приоритета")

                elif edit_choice == "0":
                    return

                else:
                    self.show_error("Неверный выбор")
            else:
                self.show_error("Неверный номер задачи")
        except ValueError:
            self.show_error("Введите число")

    def show_project_members(self):
        self.clear_screen()
        print(f"УЧАСТНИКИ ПРОЕКТА: {self.current_project['name']}")
        print("-" * 60)

        members = self.project_manager.get_project_members(self.current_project['id'])

        if not members:
            print("В проекте нет участников.")
        else:
            for member in members:
                role = "Создатель" if member['id'] == self.current_project['creator_id'] else "Участник"
                print(f"• {member['full_name']}")
                print(f"  Логин: {member['username']}")
                print(f"  Группа: {member['group_name']}")
                print(f"  Роль: {role}")
                print()

        print("-" * 60)

        if self.current_user['id'] == self.current_project['creator_id']:
            add_member = input("Добавить участника? (y/n): ").lower()
            if add_member == 'y':
                self.add_project_member()

    def add_project_member(self):
        self.clear_screen()
        print("ДОБАВЛЕНИЕ УЧАСТНИКА В ПРОЕКТ")
        print("-" * 40)

        username = input("Логин пользователя для добавления: ").strip()

        if not username:
            self.show_error("Введите логин пользователя")
            return

        success, message = self.project_manager.add_member_to_project(
            self.current_project['id'], username
        )

        if success:
            print(f"\n✓ {message}")
        else:
            self.show_error(message)

    def show_error(self, message):
        print(f"\n✗ Ошибка: {message}")

    def run(self):
        self.clear_screen()
        print("Инициализация системы...")

        if self.db.init_database():
            print("✓ База данных инициализирована")
        else:
            print("✗ Ошибка инициализации базы данных")
            return

        input("\nНажмите Enter для продолжения...")
        self.main_menu()


if __name__ == "__main__":
    app = StudentProjectCoordinator()
    app.run()