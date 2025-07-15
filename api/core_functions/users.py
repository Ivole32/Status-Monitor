import sqlite3
import bcrypt

class users:
    def __init__(self):
        self.db_path = 'users.db'
        self._initialize_database()

    def _initialize_database(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            last_login TIMESTAMP
            )'''
        )
        connection.commit()
        connection.close()

    def _get_connection(self):
        """Get a new database connection for thread safety"""
        return sqlite3.connect(self.db_path)

    def __hash_password(self, password):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        return password_hash

    def create_user(self, username, email, password):
        password_hash = self.__hash_password(password)
        
        connection = self._get_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            '''INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)''',
            (username, email, password_hash)
        )
        connection.commit()
        connection.close()

    def modify_user(self, user_id, username=None, email=None, password=None):
        connection = self._get_connection()
        cursor = connection.cursor()
        
        if username:
            cursor.execute(
                '''UPDATE users SET username = ? WHERE user_id = ?''',
                (username, user_id)
            )
        if email:
            cursor.execute(
                '''UPDATE users SET email = ? WHERE user_id = ?''',
                (email, user_id)
            )
        if password:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                '''UPDATE users SET password_hash = ? WHERE user_id = ?''',
                (password_hash, user_id)
            )
        connection.commit()
        connection.close()

    def delete_user(self, user_id):
        connection = self._get_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            '''DELETE FROM users WHERE user_id = ?''',
            (user_id,)
        )
        connection.commit()
        connection.close()

if __name__ == "__main__":
    user_manager = users()
    user_manager.create_user('testuser', 'testuser@example.com', 'securepassword')
    user_manager.modify_user(1, username='updateduser', email='updateduser@example.com', password='newpassword')
    user_manager.delete_user(1)