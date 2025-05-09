import sqlite3
import json
import os

import logging

class Database:
    def __init__(self, db_name="movie_bot.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
        try:
            self.create_tables()
            logging.info(f"База даних {self.db_name} успішно створена.")
        except Exception as e:
            logging.error(f"Помилка при ініціалізації бази даних: {e}")
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            logging.error(f"Помилка при підключенні до бази даних: {e}")
            return False
        
    def disconnect(self):
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                logging.error(f"Помилка при закритті бази даних: {e}")
            finally:
                self.conn = None
                self.cursor = None
                
    def create_tables(self):
        connect_success = self.connect()
        if not connect_success:
            logging.error("Не вдалося підключитися до бази даних.")
            return False
        
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS genres (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    api_id INTEGER,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_media (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    poster_url TEXT,
                    genre_id INTEGER,
                    media_type TEXT,
                    added_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (genre_id) REFERENCES genres(id),
                    FOREIGN KEY (added_by) REFERENCES users(id)
                )
            ''')
            self.cursor.execute('SELECT COUNT(*) FROM categories')
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                                    ("Фільми", "Повнометражні фільми"))
                self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                                    ("Серіали", "Телевізійні серіали"))
                self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                                    ("Мультфільми", "Анімаційні фільми та серіали"))
                self.conn.commit()
                logging.info("Базові категорії успішно створені.")
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Помилка при створенні таблиць: {e}")
            return False
        finally:
            self.disconnect()
            
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        if not self.connect():
            logging.error("Не вдалося підключитися до бази даних.")
            return False
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Помилка при додаванні користувача: {e}")
            return False
        finally:
            self.disconnect()
            
    def make_admin(self, user_id):
        if not self.connect():
            logging.error("Не вдалося підключитися до бази даних.")
            return False
        try:
            self.cursor.execute('''
                UPDATE users SET is_admin = 1 WHERE id = ?
            ''', (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Помилка при призначенні адміністратора: {e}")
            return False
        finally:
            self.disconnect()

    def is_admin(self, user_id):
        if not self.connect():
            logging.error("Не вдалося підключитися до бази даних.")
            return False
        try:
            self.cursor.execute('''
                SELECT is_admin FROM users WHERE id = ?
            ''', (user_id,))
            return self.cursor.fetchone()[0] == 1
        except sqlite3.Error as e:
            logging.error(f"Помилка при перевірці адміністратора: {e}")
            return False
        finally:
            self.disconnect()
            
    def get_categories(self):
        self.connect()
        self.cursor.execute('''
            SELECT id, name, description FROM categories
        ''')
        categories = self.cursor.fetchall()
        self.disconnect()
        return [{"id": c[0], "name": c[1], "description": c[2]} for c in categories]
    
    def add_category(self, name, description=""):
        self.connect()
        try:
            self.cursor.execute('''
                INSERT INTO categories (name, description) VALUES (?, ?)
            ''', (name, description))
            self.conn.commit()
            result = True
        except sqlite3.IntegrityError as e:
            logging.error(f"Помилка при додаванні категорії: {e}")
            result = False
        self.disconnect()
        return result
    
    def add_genre(self, name, api_id, category_id):
        self.connect()
        try:
            self.cursor.executre('''
                INSERT INTO genres (name, api_id, category_id) VALUES (?, ?, ?)
            ''', (name, api_id, category_id))
            self.conn.commit()
            result = True
        except sqlite3.IntegrityError as e:
            result = False
        self.disconnect()
        return result
    
    def get_genres(self, category_id=None):
        self.connect()
        if category_id:
            self.cursor.execute('''
                SELECT id, name FROM genres WHERE category_id = ?
            ''', (category_id,))
        else:
            self.cursor.execute("SELECT id, name FROM genres")
        genres = self.cursor.fetchall()
        self.disconnect()
        return [{"id": g[0], "name": g[1], "api_id": g[2]} for g in genres]
    
    def add_custom_media(self, title, description, poster_url, genre_ids, media_type, added_by):
        self.connect()
        genre_ids = json.dumps(genre_ids)
        self.cursor.execute('''
            INSERT INTO custom media
            (title, description, poster_url, genre_id, media_type, added_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, poster_url, genre_ids, media_type, added_by))
        self.conn.commit()
        self.disconnect()
        
    def get_custom_media(self, media_type=None, genre_id=None):
        self.connect()
        query = '''
            SELECT id, title, description, poster_url, genre_ids, media_type FROM custom_media
        '''
        params = []
        if media_type:
            query += ' WHERE media_type = ?'
            params.append(media_type)
        if genre_id:
            if media_type:
                query += ' AND'
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
        
db = Database()