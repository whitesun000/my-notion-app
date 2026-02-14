import streamlit as st
from app.controller import NotionController

class NotionUI:
    def __init__(self):
        # コントローラを初期化
        self.controller = NotionController()

    def render_app(self):
        st.set_page_config(page_title="Creative Manager", page_icon="✍️", layout="wide")
        st.title("✍️ Creative Manager")

        # --- サイドバー：作品管理 ---
        st.sidebar.header("📁 作品・プロジェクト")

        # 1. 新規作品登録
        with st.sidebar.expander("➕ 新しい作品を作る"):
            new_project_title = st.text_input("作品名を入力")
            if st.button("作成"):
                if new_project_title:
                    self.controller.add_project(new_project_title)
                    st.success(f"『{new_project_title}』を作成しました！")
                    st.rerun()
        
        # 2. 作品選択
        projects = self.controller.get_project()
        if not projects:
            st.info("サイドバーから作品を作成してください。")
            return
        
        project_titles = {p[1]: p[0] for p in projects}
        selected_title = st.sidebar.selectbox("編集中の作品", list(project_titles.keys()))
        selected_project_id = project_titles[selected_title]

        # --- サイドバー：エクスポート機能 ---
        st.sidebar.markdown("---") 
        st.sidebar.subheader("📤 書き出し")
        file_format = st.sidebar.selectbox(
            "保存形式を選択",
            ["Text (.txt)", "CSV (.csv)"]
        )

        # --- サイドバー：インポート機能 ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("📥 読み込み")
        uploaded_file = st.sidebar.file_opener = st.sidebar.file_uploader(
            "CSVファイルを選択", type="csv"
        )

        if uploaded_file is not None:
            if st.sidebar.button("データをインポート"):
                self.controller.import_from_csv(selected_project_id, uploaded_file)
                st.sidebar.success("読み込みが完了しました！")
                st.rerun()

        # Controllerに選択中の project_id を渡す
        data, mime, ext = self.controller.get_export_data(selected_project_id, selected_title, file_format)

        if data:
            # CSVかつExcel向けの場合は文字化け防止(BOM付き)にする
            processed_data = data.encode('utf-8-sig') if ext == "csv" else data

            st.sidebar.download_button(
                label = f"{selected_title}で保存",
                data = processed_data,
                file_name = f"{selected_title}.{ext}",
                mime = mime
            )

        
        # --- メインエリア：入力フォーム ---
        st.subheader(f"📖 作品設定: {selected_title}")
        tab1, tab2, tab3 = st.tabs(["📝 メモ・ToDo", "👤 キャラクター", "🗺️ 世界観"])

        with tab1:
            col1, col2 = st.columns([3, 1])
            content = col1.text_input("内容を入力", key="text_input")
            b_type = col2.selectbox("種類", ["テキスト", "ToDo"], key="type_select")
            if st.button("追加", key="add_text"):
                if b_type == "テキスト":
                    self.controller.add_text_block(selected_project_id, content)
                else:
                    self.controller.add_todo_block(selected_project_id, content)
                st.rerun()

        with tab2:
            c_col1, c_col2 = st.columns(2)
            c_name = c_col1.text_input("名前")
            c_role = c_col2.text_input("役割（例：主人公）")
            c_detail = st.text_area("設定詳細")
            if st.button("キャラクターを登録"):
                self.controller.add_character_block(selected_project_id, c_name, c_role, c_detail)
                st.rerun()
        
        with tab3:
            w_loc = st.text_input("場所・項目（例: 王都メルキド）")
            w_detail = st.text_area("世界観の詳細")
            if st.button("世界観設定を保存"):
                self.controller.add_world_setting_block(selected_project_id, w_loc, w_detail)
                st.rerun()

        st.divider()

        # --- 表示エリア ---
        blocks = self.controller.get_blocks_by_project(selected_project_id)

        if not blocks:
            st.info("まだこの作品に登録されたデータはありません。")
        else:
            for block in blocks:
                st.markdown(block.render())
                st.divider() 