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
        with self._get_connection() as conn:
            # 1. 作品（プロジェクト）を管理するテーブル
            conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )    
            """)

            # 2. ブロックテーブルを拡張
            # name, role, location など作品設定に必要なカラムを追加
            conn.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                block_type TEXT NOT NULL,
                content TEXT,
                is_done INTEGER DEFAULT 0,
                name TEXT,      -- キャラクター名
                role TEXT,      -- 役割
                location TEXT,  -- 場所
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
            """)
    
    # --- プロジェクト関連の操作 ---
    def save_project(self, title):
        """ 新しい作品を登録する """
        query = "INSERT INTO projects (title) VALUES (?)"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (title,))
            return cursor.lastrowid     # 新しく作ったプロジェクトIDを返す

    def fetch_all_projects(self):
        """ 全ての作品リストを取得 """
        query =  "SELECT id, title FROM projects ORDER BY created_at DESC"
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()

    # --- ブロック関連の操作 ---
    def save_block(self, block_type, content, project_id=None , is_done=0, name=None, role=None, location=None):
        """ ブロックの保存（作品IDやキャラ設定などに対応） """
        query = """
        INSERT INTO blocks (block_type, content, project_id, is_done, name, role, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(query, (block_type, content, project_id, is_done, name, role, location))

    def fetch_blocks_by_project(self, project_id):
        """ 特定の作品に紐づくブロックのみを取得する """
        query = """
        SELECT block_type, content, is_done, name, role, location
        FROM blocks
        WHERE project_id = ?
        ORDER BY created_at ASC
        """
        with self._get_connection() as conn:
            return conn.execute(query, (project_id,)).fetchall()
        
    def fetch_all_blocks(self):
        """ 全てのブロックを取得 """
        query = "SELECT block_type, content, is_done, name, role, location FROM blocks ORDER BY created_at ASC"
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()