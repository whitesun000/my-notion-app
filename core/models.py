from abc import ABC, abstractmethod
from datetime import datetime

# --- 抽象クラス：すべてのブロックの「親」---
class BaseBlock(ABC):
    def __init__(self):
        self.created_at = datetime.now()

    @abstractmethod
    def render(self):
        """ 画面に表示するためのメソッド（子クラスで必ず実装する） """
        pass

# --- 継承：テキスト入力用のブロック ---
class TextBlock(BaseBlock):
    def __init__(self, content=""):
        super().__init__()
        self.content = content

    def render(self):
        return f"Text: {self.content}"

# --- 継承：ToDoリスト用のブロック ---
class TodoBlock(BaseBlock):
    def __init__(self, task="", is_done=False):
        super().__init__()
        self.task = task
        self.is_done = is_done
    
    def render(self):
        status = "✅" if self.is_done else "⬜"
        return f"{status} {self.task}"