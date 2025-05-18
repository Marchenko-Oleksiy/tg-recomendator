import sqlite3
import json
import os
import logging

class Database:
    def __init__(self, db_name="movie_bot.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
        # Перевіряємо справність бази даних
        try:
            self.create_tables()
            logging.info(f"База даних {db_name} успішно ініціалізована")
        except sqlite3.Error as e:
            logging.error(f"Помилка при ініціалізації бази даних: {e}")
    
    def connect(self):
        """З'єднання з базою даних"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            logging.error(f"Помилка з'єднання з базою даних: {e}")
            return False
    
    def disconnect(self):
        """Відключення від бази даних"""
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                logging.error(f"Помилка відключення від бази даних: {e}")
            finally:
                self.conn = None
                self.cursor = None
    
    def create_tables(self):
        """Створення необхідних таблиць"""
        connect_success = self.connect()
        if not connect_success:
            logging.error("Не вдалося підключитися до бази даних для створення таблиць")
            return False
        
        try:
            # Таблиця користувачів
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Таблиця категорій
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Таблиця жанрів
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                api_id INTEGER,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
            ''')
            
            # Таблиця користувацьких фільмів/серіалів
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_media (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                poster_url TEXT,
                genre_ids TEXT, 
                media_type TEXT,
                added_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (added_by) REFERENCES users (id)
            )
            ''')
            
            # Вставляємо початкові категорії, якщо їх немає
            self.cursor.execute("SELECT COUNT(*) FROM categories")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", 
                    ("Фільми", "Повнометражні фільми"))
                self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", 
                    ("Серіали", "Телевізійні серіали"))
                self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", 
                    ("Мультфільми", "Анімаційні фільми та серіали"))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Помилка при створенні таблиць: {e}")
            return False
        finally:
            self.disconnect()
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Додати нового користувача або оновити існуючого"""
        if not self.connect():
            return False
        
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO users (id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, last_name)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Помилка при додаванні користувача: {e}")
            return False
        finally:
            self.disconnect()
    
    def make_admin(self, user_id):
        """Зробити користувача адміністратором"""
        if not self.connect():
            return False
        
        try:
            self.cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Помилка при призначенні адміністратора: {e}")
            return False
        finally:
            self.disconnect()
    
    def is_admin(self, user_id):
        """Перевірити, чи є користувач адміністратором"""
        if not self.connect():
            return False
        
        try:
            self.cursor.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
            result = self.cursor.fetchone()
            return result and result[0] == 1
        except sqlite3.Error as e:
            logging.error(f"Помилка при перевірці адміністратора: {e}")
            return False
        finally:
            self.disconnect()
    
    def get_categories(self):
        """Отримати всі категорії"""
        self.connect()
        self.cursor.execute("SELECT id, name, description FROM categories")
        categories = self.cursor.fetchall()
        self.disconnect()
        return [{"id": c[0], "name": c[1], "description": c[2]} for c in categories]
    
    def add_category(self, name, description=""):
        """Додати нову категорію"""
        self.connect()
        try:
            self.cursor.execute(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (name, description)
            )
            self.conn.commit()
            result = True
        except sqlite3.IntegrityError:
            result = False
        self.disconnect()
        return result
    
    def add_genre(self, name, api_id, category_id):
        """Додати новий жанр"""
        self.connect()
        try:
            self.cursor.execute(
                "INSERT INTO genres (name, api_id, category_id) VALUES (?, ?, ?)",
                (name, api_id, category_id)
            )
            self.conn.commit()
            result = True
        except sqlite3.IntegrityError:
            result = False
        self.disconnect()
        return result
    
    def get_genres(self, category_id=None):
        """Отримати всі жанри для вказаної категорії"""
        self.connect()
        if category_id:
            self.cursor.execute(
                "SELECT id, name, api_id FROM genres WHERE category_id = ?", 
                (category_id,)
            )
        else:
            self.cursor.execute("SELECT id, name, api_id FROM genres")
        
        genres = self.cursor.fetchall()
        self.disconnect()
        return [{"id": g[0], "name": g[1], "api_id": g[2]} for g in genres]
    
    def add_custom_media(self, title, description, poster_url, genre_ids, media_type, added_by):
        """Додати власний фільм/серіал"""
        self.connect()
        genre_ids_str = json.dumps(genre_ids)
        self.cursor.execute(
            "INSERT INTO custom_media (title, description, poster_url, genre_ids, media_type, added_by) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, poster_url, genre_ids_str, media_type, added_by)
        )
        self.conn.commit()
        self.disconnect()
    
    def get_custom_media(self, media_type=None, genre_id=None):
        """Отримати медіа за типом та/або жанром"""
        self.connect()
        query = "SELECT id, title, description, poster_url, genre_ids, media_type FROM custom_media"
        params = []
        
        if media_type or genre_id:
            query += " WHERE"
        
        if media_type:
            query += " media_type = ?"
            params.append(media_type)
        
        if genre_id:
            if media_type:
                query += " AND"
            query += " json_extract(genre_ids, '$') LIKE ?"
            params.append(f'%{genre_id}%')
        
        self.cursor.execute(query, params)
        media = self.cursor.fetchall()
        self.disconnect()
        
        return [{
            "id": m[0],
            "title": m[1],
            "description": m[2],
            "poster_url": m[3],
            "genre_ids": json.loads(m[4]) if m[4] else [],
            "media_type": m[5]
        } for m in media]

# Ініціалізуємо базу даних
db = Database() 