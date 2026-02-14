import csv
import io

from core.models import TextBlock, TodoBlock, CharacterBlock, WorldSettingBlock
from core.database import DatabaseManager
from datetime import datetime

class NotionController:
    def __init__(self):
        # データベース操作クラスをインスタンス化（カプセル化）
        self.db = DatabaseManager()

    # --- 作品（プロジェクト）管理 ---
    def add_project(self, title):
        """ 新しい作品を作成する """
        if title.strip():
            return self.db.save_project(title)

    def get_project(self):
        """ 全ての作品リストを取得する """
        return self.db.fetch_all_projects()
    
    # --- ブロック追加（プロジェクトID指定）---
    def add_text_block(self, project_id, content):
        """ テキストブロックを作成して保存する """
        if content.strip():
            self.db.save_block("text", content, project_id=project_id)

    def add_todo_block(self, project_id, task, is_done=False):
        """ ToDoブロックを作成して保存する """
        if task.strip():
            # SQLiteに合わせてTrue/Falseを1/0に変換
            status = 1 if is_done else 0
            self.db.save_block("todo", task, project_id=project_id, is_done=status)

    def add_character_block(self, project_id, name, role, content):
        if name.strip():
            self.db.save_block("character", content, project_id=project_id, name=name, role=role)
    
    def add_world_setting_block(self, project_id, location, content):
        if location.strip():
            self.db.save_block("world", content, project_id=project_id, location=location)

    # --- データ取得 ---
    def get_blocks_by_project(self, project_id):
        """ 指定された作品のデータを取得し、適切なクラスに変換する """
        raw_data = self.db.fetch_blocks_by_project(project_id)
        blocks = []

        for b_type, content, is_done, name, role, loc in raw_data:
            if b_type == "text":
                blocks.append(TextBlock(content))
            elif b_type == "todo":
                blocks.append(TodoBlock(content, bool(is_done)))
            elif b_type == "character":
                blocks.append(CharacterBlock(name, role, content))
            elif b_type == "world":
                blocks.append(WorldSettingBlock(loc, content))
        
        return blocks

    # --- エクスポート関連 ---    
    def get_export_data(self, project_id, project_title, file_format):
        """ 選択中の作品データを指定形式で返す """
        blocks = self.get_blocks_by_project(project_id)

        if file_format == "Text (.txt)":
            return self._format_as_txt(blocks, project_title), "text/plain", "txt"
        elif file_format == "CSV (.csv)":
            return self._format_as_csv(blocks), "text/csv", "csv"
        return None, None, None
    
    def _format_as_txt(self, blocks, project_title):
        if not blocks: return "データがありません。"
        output = f"--- Export: {project_title} ---\n"
        output += f"日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for block in blocks:
            output += block.render() + "\n"
            output += "-" * 20 + "\n"
        return output

    def _format_as_csv(self, blocks):
        if not blocks: 
            return ""
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["タイプ", "内容", "完了/名前", "役割/場所"])
        for b in blocks:
            b_type = b.__class__.__name__
            # クラスによってCSVに入れる値を変える
            val1, val2 = "", ""
            if isinstance(b, TodoBlock):
                val1 = "完了" if b.is_done else "未完了"
            elif isinstance(b, CharacterBlock): val1, val2 = b.name, b.role
            elif isinstance(b, WorldSettingBlock): val1 = b.location
            
            writer.writerow([b_type, b.content, val1, val2])
        return output.getvalue()
    
    def import_from_csv(self, project_id, uploaded_file):
        """ CSVファイルを読み込んでDBに保存する """
        # ファイルをテキストモードで読み込む
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8-sig"))
        reader = csv.reader(stringio)

        # ヘッダー（1行目）を飛ばす
        next(reader, None)

        for row in reader:
            # CSVの列構成:　[タイプ, 内容, 完了/名前, 役割/場所]
            if len(row) < 2: continue

            b_type = row[0]
            content = row[1]
            val1 = row[2] if len(row) > 2 else ""
            val2 = row[3] if len(row) > 3 else ""

            # タイプに応じて保存
            if b_type == "TextBlock":
                self.add_text_block(project_id, content)
            elif b_type == "TodoBlock":
                is_done = (val1 == "完了")
                self.add_todo_block(project_id, content, is_done)
            elif b_type == "CharacterBlock":
                self.add_character_block(project_id, val1, val2, content)
            elif b_type == "WorldSettingBlock":
                self.add_world_setting_block(project_id, val1, content)
