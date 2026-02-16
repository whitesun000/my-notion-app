import streamlit as st
from app.controller import NotionController

class NotionUI:
    def __init__(self):
        # コントローラを初期化
        self.controller = NotionController()

    def render_app(self):
        st.set_page_config(page_title="Creative Manager", page_icon="✍️", layout="wide")
        st.markdown(self.controller.get_style(), unsafe_allow_html=True)
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
        selected_title = st.sidebar.selectbox("編集中の作品", options=project_titles.keys())
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
        tab1, tab2, tab3, tab4 = st.tabs(["📝 メモ・ToDo", "👤 キャラクター", "🗺️ 世界観", "📌 プロット・構成"])

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
        
        with tab4:
            s_title = st.text_input("項目名（例：全体の流れ、後半の展開など）")
            s_content = st.text_area("内容（プロットや下書き）", height=300)
            if st.button("プロットを保存"):
                self.controller.add_story_block(selected_project_id, s_title, s_content)
                st.rerun()

        st.divider()

        # --- 本編執筆エリア ---
        st.header(f"✒️ 本編執筆: {selected_title}")
        
        # 1. 章（大項目）の管理
        col_ch_create, col_ep_create = st.columns(2)

        with col_ch_create.expander("📁 新しい章（大項目）を追加"):
            new_ch_title = st.text_input("章名（例：第一章 旅立ち）", key="new_ch_input")
            if st.button("章を作成", key="btn_create_ch"):
                success, msg = self.controller.add_chapter(selected_project_id, new_ch_title)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        # 章の一覧を取得                    
        chapters = self.controller.get_chapters(selected_project_id)

        if not chapters:
            st.info("「章」を作成してください。")
        else:
            # 章を選択
            ch_options = {c[1]: c[0] for c in chapters}
            selected_ch_name = st.selectbox("📁 編集する章を選択", options=ch_options.keys(),key="sel_ch")
            selected_ch_id = ch_options[selected_ch_name]

            # 章タイトル編集用
            with st.expander("📝 章の名前を変更する"):
                new_ch_name = st.text_input("新しい章名", value=selected_ch_name)
                if st.button("章名を変更"):
                    self.controller.update_chapter_title(selected_ch_id, new_ch_name)
                    st.success("章名を変更しました")
                    st.rerun()

            # 2. 話（エピソード）の管理
            with col_ep_create.expander("📜 新しい話（エピソード）を追加"):
                new_ep_title = st.text_input("話名（例：第一話 出会い）", key="new_ep_input")
                if st.button("話を作成", key="btn_create_ep"):
                    success, msg = self.controller.add_episode(selected_ch_id, new_ep_title)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            # 選択中の章に紐づく話を取得
            episodes = self.controller.get_episodes(selected_ch_id)

            if not episodes:
                st.info(f"「{selected_ch_name}」にはまだ話がありません。")

            else:
                # 話を選択
                ep_options = {f"第{i+1}話: {e[1]}": e for i, e in enumerate(episodes)}
                selected_ep_label = st.selectbox("📜 編集する話を選択", options=ep_options.keys(), key="sel_ep")
                target_ep = ep_options[selected_ep_label]
                ep_id, ep_title, ep_content = target_ep[0], target_ep[1], target_ep[2]        

                # 3. 執筆・表示モード
                mode = st.radio("表示モード", ["編集", "プレビュー・横書き", "プレビュー・縦書き"], horizontal=True, key="p_mode")

                if mode == "編集":
                    edit_t = st.text_input("タイトルを編集", value=ep_title, key=f"t_{ep_id}")
                    edit_c = st.text_area("本文を編集", value=ep_content, height=500, key=f"c_ep_{ep_id}")

                    col_save, col_del = st.columns([1, 1])
                    if col_save.button("💾 上書き保存", key=f"save_{ep_id}"):
                        with st.spinner("保存中..."):
                            self.controller.update_episode(ep_id, edit_t, edit_c)    
                            st.toast(f"「{edit_t}」を上書き保存しました！", icon="✅")
                        
                    if col_del.button("🗑️ この話を削除", key=f"del_ep_{ep_id}"):
                        with st.spinner("削除中..."):
                            self.controller.delete_episode(ep_id)
                            st.toast("削除が完了しました", icon="🗑️")
                        st.balloons()
                        st.rerun()

                else:
                    # プレビュー表示
                    style_class = "vertical-mode" if "縦書き" in mode else "horizontal-mode"
                    st.markdown(f"### {ep_title}")
                    # HTMLでプレビューを表示
                    st.markdown(
                        f'<div class="preview-container {style_class}">{ep_content}</div>', unsafe_allow_html=True
                    )

        # --- 表示エリア ---
        st.subheader("📌 設定・メモ一覧")
        all_blocks = self.controller.get_blocks_by_project(selected_project_id)

        list_tab1, list_tab2, list_tab3, list_tab4 = st.tabs(["📝 メモ・ToDo", "👤 キャラクター", "🗺️ 世界観", "📌 プロット・構成"])

        for block in all_blocks:
            b_id = getattr(block, 'id', None)
            target_tab = None
            if block.__class__.__name__ in ["TextBlock", "TodoBlock"]: target_tab = list_tab1
            elif block.__class__.__name__ == "CharacterBlock": target_tab = list_tab2
            elif block.__class__.__name__ == "WorldSettingBlock": target_tab = list_tab3
            elif block.__class__.__name__ == "StoryBlock": target_tab = list_tab4

            if target_tab:
                with target_tab:
                    with st.expander(f"🔍 {block.render().splitlines()[0]}"):
                        if block.__class__.__name__ == "CharacterBlock":
                            edit_name = st.text_input("名前", value=block.name, key=f"name_{b_id}")
                            edit_role = st.text_input("役割", value=block.role, key=f"role_{b_id}")
                            edit_cont = st.text_area("詳細", value=block.content, key=f"cont_{b_id}")
                            if st.button("保存", key=f"btn_{b_id}"):
                                self.controller.db.update_block(b_id, edit_cont, name=edit_name, role=edit_role)
                                st.rerun()

                        elif block.__class__.__name__ == "WorldSettingBlock":
                            edit_loc = st.text_input("場所", value=block.location, key=f"loc_{b_id}")
                            edit_cont = st.text_area("詳細", value=block.content, key=f"cont_{b_id}")
                            if st.button("保存", key=f"btn_{b_id}"):
                                self.controller.db.update_block(b_id, edit_cont, location=edit_loc)
                                st.rerun()
                        
                        else:
                            # 通常のテキスト・ToDo
                            edit_cont = st.text_area("内容", value=block.content, key=f"cont_{b_id}")
                            if st.button("保存", key=f"btn_{b_id}"):
                                self.controller.db.update_block(b_id, edit_cont)
                                st.rerun()
                            
                        if st.button("🗑️ 削除", key=f"del_{b_id}"):
                            self.controller.delete_block(b_id)
                            st.rerun()
        