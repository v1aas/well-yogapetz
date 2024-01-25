import asyncio
import inquirer
from inquirer import prompt
from manager_db import DatabaseManager
from well import complete_tasks_well, complete_daily_tasks, update_invites, claim_books, get_all_stats_book, update_token, intro, check_and_complete_tasks

db_manager = DatabaseManager()
db_manager.connect()
db_manager.create_tables()

def main():
    intro()
    while True:
        questions = [
            inquirer.List('choice',
                        message="Доступные модули",
                        choices=[
                            'Выполнение всех заданий',
                            'Выполнение дейли заданий',
                            'Проверка всех заданий',
                            'Минт книжек',
                            'Статистика всех книг на аккаунтах',
                            'Обновление инвайтов',
                            'Обновление токена в БД',
                            'Выход'
                            ])
        ]
        
        choice = prompt(questions)['choice']

        if choice == 'Выполнение всех заданий':
            asyncio.run(complete_tasks_well())
        elif choice == 'Выполнение дейли заданий':
            asyncio.run(complete_daily_tasks())
        elif choice == 'Проверка всех заданий':
            asyncio.run(check_and_complete_tasks())
        elif choice == 'Минт книжек':
            asyncio.run(claim_books())
        elif choice == 'Статистика всех книг на аккаунтах':
            get_all_stats_book()
        elif choice == 'Обновление инвайтов':
            asyncio.run(update_invites())
        elif choice == 'Обновление токена в БД':
            update_token()
        else:
            print("Выход")
            break

if __name__ == '__main__':
    main()
    