import sqlite3
from loguru import logger

class DatabaseManager:
    def __init__(self, db_name='accounts.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def commit_changes(self):
        self.conn.commit()
    
    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                                token TEXT PRIMARY KEY,
                                private_key TEXT UNIQUE
                            )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                                token TEXT PRIMARY KEY,
                                uncommon INTEGER,
                                rare INTEGER,
                                legendary INTEGER,
                                mythical INTEGER,
                                FOREIGN KEY (token) REFERENCES accounts(token)
                            )''')

    def save_account(self, token, key):
        self.cursor.execute('''INSERT INTO accounts (token, private_key) VALUES (?, ?)''', (token, key))
        self.commit_changes()
        
    def update_token(self, old_token, new_token):
        self.cursor.execute('''SELECT COUNT(*) FROM accounts WHERE token = ?''', (old_token,))
        count = self.cursor.fetchone()[0]
        if count > 0:
            self.cursor.execute('''UPDATE accounts SET token = ? WHERE token = ?''', (new_token, old_token))
            self.commit_changes()
            logger.success(f"Токен {old_token} успешно обновлен на {new_token}")
        else:
            logger.error(f"Ошибка: Токен {old_token} не найден в таблице.")
    
    def save_books(self, private_key, uncommon, rare, legendary, mythical):
        self.cursor.execute('''SELECT token FROM accounts WHERE private_key = ?''', (private_key,))
        token = self.cursor.fetchone()[0]
        if token:
            self.cursor.execute('''SELECT * FROM books WHERE token = ?''', (token,))
            existing_record = self.cursor.fetchone()
            if existing_record:
                self.cursor.execute('''UPDATE books 
                                        SET uncommon = ?, 
                                            rare = ?, 
                                            legendary = ?, 
                                            mythical = ? 
                                        WHERE token = ?''',
                                    (uncommon, rare, legendary, mythical, token))
            else:
                self.cursor.execute('''INSERT INTO books (token, uncommon, rare, legendary, mythical) 
                                        VALUES (?, ?, ?, ?, ?)''',
                                    (token, uncommon, rare, legendary, mythical))
            self.commit_changes()
        else:
            logger.error(f"Токен для адреса в БД не найден.")
    
    def get_accounts(self):
        self.cursor.execute('''SELECT token, private_key FROM accounts''')
        return self.cursor.fetchall()
    
    def get_all_stats_book(self):
        self.cursor.execute('''SELECT SUM(uncommon), SUM(rare), SUM(legendary), SUM(mythical) FROM books''')
        return self.cursor.fetchall()
    
    def get_stats_of_all_accounts(self):
        self.cursor.execute('''SELECT a.token, a.private_key, b.uncommon, b.rare, b.legendary, b.mythical
                            FROM accounts a
                            LEFT JOIN books b ON a.token = b.token''')
        return self.cursor.fetchall()
    