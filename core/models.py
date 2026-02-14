from abc import ABC, abstractmethod
from datetime import datetime

# --- 抽象クラス：すべてのブロックの「親」---
class BaseBlock(ABC):
    def __init__(self, content="", id=None, created_at=None):
        # 共通の属性はすべて親クラスで管理する
        self.id = id
        self.content = content # ← これを共通名にする
        self.created_at = created_at or datetime.now()

    @abstractmethod
    def render(self):
        """ 画面に表示するためのメソッド（子クラスで必ず実装する） """
        pass

# --- 継承：テキスト入力用のブロック ---
class TextBlock(BaseBlock):
    def render(self):
        return f"Text: {self.content}"

# --- 継承：ToDoリスト用のブロック ---
class TodoBlock(BaseBlock):
    def __init__(self, content="", is_done=False, **kwargs):
        super().__init__(content, **kwargs)
        self.is_done = is_done
    
    def render(self):
        status = "✅" if self.is_done else "⬜"
        return f"{status} {self.content}"
    
# --- 作品用管理用のクラス ---
class CharacterBlock(BaseBlock):
    def __init__(self, name, role, content, **kwargs):
        # content には「性格・外見」などの詳細を入れる想定
        super().__init__(content, **kwargs)
        self.name = name
        self.role = role # 主人公、ライバル、村人Ａなど
    
    def render(self):
        return f"👤 **キャラ名: {self.name}** ({self.role})\n\n設定: {self.content}"
    
class WorldSettingBlock(BaseBlock):
    def __init__(self, location, content, **kwargs):
        super().__init__(content, **kwargs)
        self.location = location
    
    def render(self):
        return f"🗺️ **場所・項目: {self.location}**\n\n詳細: {self.content}"