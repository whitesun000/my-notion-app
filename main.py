from app.ui import NotionUI

def main():
    # UIクラスを生成して実行
    app = NotionUI()
    app.render_app()

if __name__ == "__main__":
    main()