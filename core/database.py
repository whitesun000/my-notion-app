import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="data/notion_app.db"):
        self.db_path = db_path
        # data フォルダがない場合に備えて作成
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()
    
    def _get_connection(self):
        """ データベースへの接続を取得する（内部用メソッド） """
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        """ テーブルの初期設定  """
        query = """
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_type TEXT NOT NULL,
            content TEXT,
            is_done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        with self._get_connection() as conn:
            conn.execute(query)
        
    def save_block(self, block_type, content, is_done=0):
        """ ブロックの保存 """
        query = "INSERT INTO blocks (block_type, content, is_done) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (block_type, content, is_done))
        
    def fetch_all_blocks(self):
        """ 全てのブロックを取得 """
        query = "SELECT block_type, content, is_done FROM blocks ORDER BY created_at ASC"
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()