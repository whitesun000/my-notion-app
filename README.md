# Creative Manager (Novel Writing & Setting Manager) ✍️

PythonとStreamlitで作成した、小説執筆と設定管理のためのクリエイティブ支援ツールです。
「章（Chapter） > 話（Episode）」の階層構造による本格的な執筆管理が可能です。

## 特徴
- **階層型執筆システム**: 「章」と「話」を分離した本格的なデータベース設計。
- **統合設定管理**: 
  - キャラクター、世界観、プロット、ToDoをタブ形式で整理。
  - キャラクター名や場所などの属性を個別に管理・編集可能。
- **クリーンな設計 ([2026-02-05] リファクタリング済)**:
  - **MVCモデル**: UI（Streamlit）、Controller、Model/Databaseの責務を分離。
  - **オブジェクト指向**: 継承・カプセル化を活用した、拡張性の高いブロックシステム。
- **プレビュー機能**: 執筆中のテキストを横書き・縦書きでプレビュー可能。
- **データポータビリティ**: CSVインポート/エクスポート機能。

## 使い方
1. ライブラリのインストール
   `pip install -r requirements.txt`
2. アプリの起動
   `streamlit run main.py`

## 技術スタック
- **Frontend/UI**: Streamlit
- **Backend**: Python 3.12+
- **Database**: SQLite3

⚠️ Disclaimer (免責事項)
本プロジェクトは教育およびセキュリティ研究を目的としています。
許可されていない対象に対して本ツールを使用することは違法行為となります。
本ツールの使用によって生じた直接的・間接的な損害について、作者は一切の責任を負いません。

⚠️ Disclaimer
This project is for educational and security research purposes only.
Using this tool against targets without prior authorization is illegal.
The author assumes no liability and is not responsible for any direct or indirect damage caused by the use of this tool.