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

            # 3. 章（Chapter）を管理するテーブル
            conn.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                title TEXT NOT NULL,
                order_num INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
            """)

            # 4. 話（Episode）を管理するテーブル - 「中項目 - 本文」として使用
            conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER,
                title TEXT NOT NULL,
                content TEXT,
                order_num INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapters (id)
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

    def update_block(self, block_id, content, **kwargs):
        """ 指定したIDブロックを更新する """
        # kwargsから動的に更新カラムを作る（少し高度なリファクタリング）
        keys = ["content"] + list(kwargs.keys())
        values = [content] + list(kwargs.values())
        set_clause = ", ".join([f"{k} = ?" for k in keys])

        query = f"UPDATE blocks SET {set_clause} WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, values + [block_id])

    def delete_block(self, block_id):
        """ 指定したIDのブロックを削除する """
        query = "DELETE FROM blocks WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (block_id,))

    def fetch_blocks_by_project(self, project_id):
        """ 特定の作品に紐づくブロックのみを取得する """
        query = """
        SELECT id, block_type, content, is_done, name, role, location
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
        
    # --- 章（Chapter）操作用のメソッド ---
    def save_chapter(self, project_id, title):
        query = "INSERT INTO chapters (project_id, title) VALUES (?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (project_id, title))

    def fetch_chapters_by_project(self, project_id):
        query = "SELECT id, title FROM chapters WHERE project_id = ? ORDER BY order_num ASC, id ASC"
        with self._get_connection() as conn:
            return conn.execute(query, (project_id,)).fetchall()
        
    def update_chapter_title(self, chapter_id, title):
        query = "UPDATE chapter SET title = ? WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (title, chapter_id))
            return True

    # --- 話（Episode）を操作用 ---
    def save_episode(self, chapter_id, title, content):
        query = "INSERT INTO episodes (chapter_id, title, content) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (chapter_id, title, content))
    
    def fetch_episodes_by_chapter(self, chapter_id):
        query = "SELECT id, title, content FROM episodes WHERE chapter_id = ? ORDER BY order_num ASC, id ASC"
        with self._get_connection() as conn:
            return conn.execute(query, (chapter_id,)).fetchall()
        
    def update_episode(self, episode_id, title, content):
        try:
            query = "UPDATE episodes SET title = ?, content = ? WHERE id = ?"
            with self._get_connection() as conn:
                conn.execute(query, (title, content, episode_id))
            return True
        except Exception:
            return False

    def delete_episode(self, episode_id):
        query = "DELETE FROM episodes WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (episode_id,))
