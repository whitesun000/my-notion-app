import streamlit as st
from app.controller import NotionController

class NotionUI:
    def __init__(self):
        # コントローラを初期化
        self.controller = NotionController()

    def render_app(self):
        st.set_page_config(page_title="My Personal Notion", page_icon="📝")
        st.title("📝 My Personal Notion")

        # --- サイドバー：新しいブロックの追加 ---
        st.sidebar.header("ブロックを追加")
        block_type = st.sidebar.selectbox("種類を選択", ["テキスト", "ToDoリスト"])

        input_text = st.sidebar.text_area("内容を入力")

        if st.sidebar.button("追加"):
            if block_type == "テキスト":
                self.controller.add_text_block(input_text)
            else:
                self.controller.add_todo_block(input_text)
            st.rerun() # 画面を更新
        
        # --- メインエリア：データの表示 ---
        st.subheader("マイページ")
        blocks = self.controller.get_all_blocks_for_display()

        if not blocks:
            st.info("まだブロックがありません。サイドバーから追加してください。")
        else:
            for block in blocks:
                # 各モデルの render() メソッドを呼び出す（ポリモーフィズム）
                st.write(block.render())
                st.divider() # 区切り線