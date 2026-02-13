from core.models import TextBlock, TodoBlock
from core.database import DatabaseManager

class NotionController:
    def __init__(self):
        # データベース操作クラスをインスタンス化（カプセル化）
        self.db = DatabaseManager()

    def add_text_block(self, content):
        """ テキストブロックを作成して保存する """
        if content.strip():
            self.db.save_block("text", content)

    def add_todo_block(self, task, is_done=False):
        """ ToDoブロックを作成して保存する """
        if task.strip():
            # SQLiteに合わせてTrue/Falseを1/0に変換
            status = 1 if is_done else 0
            self.db.save_block("todo", task, status)
    
    def get_all_blocks_for_display(self):
        """
        DBからデータを取得し適切なModelクラスのインスタンに変換して返す
        """
        raw_data = self.db.fetch_all_blocks()
        blocks = []

        for block_type, content, is_done in raw_data:
            if block_type == "text":
                blocks.append(TextBlock(content))
            elif block_type == "todo":
                blocks.append(TodoBlock(content, bool(is_done)))
            
        return blocks