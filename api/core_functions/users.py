import sqlite3
import bcrypt

class users:
    def __init__(self):
        self.connection = sqlite3.connect('users.db')
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            last_login TIMESTAMP,
            )'''
        )
        self.connection.commit()

    def create_user(self, username, email, password):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        self.cursor.execute(
            '''INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)''',
            (username, email, password_hash)
        )
        self.connection.commit()

    def modify_user(self, user_id, username=None, email=None, password=None):
        if username:
            self.cursor.execute(
                '''UPDATE users SET username = ? WHERE user_id = ?''',
                (username, user_id)
            )
        if email:
            self.cursor.execute(
                '''UPDATE users SET email = ? WHERE user_id = ?''',
                (email, user_id)
            )
        if password:
            password_hash, password_salt = self.hash_password(password)
            self.cursor.execute(
                '''UPDATE users SET password_hash = ?, password_salt = ? WHERE user_id = ?''',
                (password_hash, password_salt, user_id)
            )
        self.connection.commit()

    def delete_user(self, user_id):
        self.cursor.execute(
            '''DELETE FROM users WHERE user_id = ?''',
            (user_id,)
        )
        self.connection.commit()

if __name__ == "__main__":
    user_manager = users()
    user_manager.create_user('testuser', 'testuser@example.com', 'securepassword')
    user_manager.modify_user(1, username='updateduser', email='updateduser@example.com', password='newpassword')
    user_manager.delete_user(1)