#!/usr/bin/env python
"""
ローカル環境で音声文字起こし・要約Q&Aアプリケーションを実行するスクリプト
"""
import os
import sys
import subprocess
import webbrowser
import time
from dotenv import load_dotenv

def check_environment():
    """環境をチェックする"""
    print("🔍 環境を確認しています...")
    
    # 必要なディレクトリが存在するか確認
    directories = ['static', 'static/uploads', 'templates']
    missing_dirs = [d for d in directories if not os.path.exists(d)]
    
    if missing_dirs:
        print(f"❌ 必要なディレクトリが見つかりません: {', '.join(missing_dirs)}")
        return False
    
    # 必要なファイルが存在するか確認
    required_files = ['app.py', 'requirements.txt', 'setup.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 必要なファイルが見つかりません: {', '.join(missing_files)}")
        return False
    
    # .envファイルが存在するか確認
    if not os.path.exists('.env'):
        print("⚠️ .envファイルが見つかりません。セットアップ時に作成されます。")
    else:
        # .envが存在する場合は読み込む
        load_dotenv()
        print("✅ .envファイルを読み込みました")
    
    return True

def setup_local_environment():
    """ローカル環境をセットアップする"""
    print("🔧 ローカル環境のセットアップを開始します...")
    
    # Pythonバージョンを確認
    python_version = sys.version_info
    print(f"📌 Python バージョン: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8以上が必要です")
        return False
    
    # 仮想環境を作成するか確認
    create_venv = input("仮想環境を作成しますか？ (y/n): ").lower() == 'y'
    
    if create_venv:
        venv_name = "venv"
        print(f"🔧 仮想環境 '{venv_name}' を作成しています...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_name])
            print(f"✅ 仮想環境 '{venv_name}' を作成しました")
            
            # 仮想環境のPythonパス
            if os.name == 'nt':  # Windows
                venv_python = os.path.join(venv_name, "Scripts", "python.exe")
            else:  # macOS/Linux
                venv_python = os.path.join(venv_name, "bin", "python")
            
            # 依存関係をインストール
            print("📦 必要なパッケージをインストールしています...")
            subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ パッケージのインストールが完了しました")
            
            # 仮想環境のアクティベート方法を表示
            if os.name == 'nt':  # Windows
                activate_cmd = f"{venv_name}\\Scripts\\activate"
            else:  # macOS/Linux
                activate_cmd = f"source {venv_name}/bin/activate"
            
            print(f"\n🔔 使用する前に仮想環境をアクティベートしてください:")
            print(f"    {activate_cmd}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 仮想環境の作成に失敗しました: {e}")
            return False
    else:
        # グローバル環境に直接インストール
        print("📦 必要なパッケージをグローバル環境にインストールしています...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ パッケージのインストールが完了しました")
        except subprocess.CalledProcessError as e:
            print(f"❌ パッケージのインストールに失敗しました: {e}")
            return False
    
    # セットアップスクリプトを実行
    try:
        subprocess.check_call([sys.executable, "setup.py"])
    except subprocess.CalledProcessError as e:
        print(f"❌ セットアップスクリプトの実行に失敗しました: {e}")
        return False
    
    print("\n✅ ローカル環境のセットアップが完了しました！")
    return True

def check_api_keys():
    """APIキーの設定を確認する"""
    print("🔑 APIキーの設定を確認しています...")
    
    # 必要なAPIキーのリスト
    api_keys = [
        "OPENAI_API_KEY",
        "DEEPGRAM_API_KEY",
        "GROQ_API_KEY",
        "AZURE_OPENAI_KEY",
        "AZURE_OPENAI_ENDPOINT"
    ]
    
    missing_keys = []
    
    # 環境変数からAPIキーを確認
    for key in api_keys:
        value = os.environ.get(key)
        if value:
            print(f"✅ {key} は設定されています")
        else:
            print(f"❌ {key} が設定されていません")
            missing_keys.append(key)
    
    if missing_keys:
        print("\n⚠️ 以下のAPIキーが設定されていません:")
        for key in missing_keys:
            print(f"  - {key}")
        print("\n.envファイルを編集して、これらのAPIキーを設定してください。")
        return False
    
    return True

def run_app(port=5000):
    """アプリケーションを実行する"""
    print(f"🚀 ポート {port} でアプリケーションを起動しています...")
    
    try:
        # URLをブラウザで開く（少し遅延させる）
        def open_browser():
            time.sleep(2)
            url = f"http://localhost:{port}"
            print(f"🌐 ブラウザで {url} を開いています...")
            webbrowser.open(url)
        
        import threading
        threading.Thread(target=open_browser).start()
        
        # Flaskアプリケーションを実行
        os.environ["FLASK_APP"] = "app.py"
        subprocess.check_call([sys.executable, "-m", "flask", "run", "--port", str(port)])
        
    except KeyboardInterrupt:
        print("\n👋 アプリケーションを停止しました")
    except subprocess.CalledProcessError as e:
        print(f"❌ アプリケーションの実行に失敗しました: {e}")
        return False
    
    return True

def main():
    """メイン実行関数"""
    print("=" * 50)
    print("🔊 音声文字起こし・要約Q&Aアプリケーション 🔊")
    print("=" * 50)
    
    # 環境チェック
    if not check_environment():
        setup_choice = input("環境のセットアップを行いますか？ (y/n): ").lower() == 'y'
        if setup_choice:
            if not setup_local_environment():
                print("❌ セットアップに失敗しました。問題を修正してから再度実行してください。")
                return
        else:
            print("❌ セットアップをスキップしました。必要なファイルや環境が揃っていない可能性があります。")
            return
    
    # APIキーのチェック
    if not check_api_keys():
        update_keys = input("APIキーを設定してから続行しますか？ (y/n): ").lower() == 'y'
        if update_keys:
            print("📝 .envファイルを編集してから、再度実行してください。")
            return
        else:
            print("⚠️ APIキーが不足したままアプリケーションを実行します。一部の機能が動作しない可能性があります。")
    
    # ポート番号の選択
    port = 5000
    try:
        port_input = input(f"使用するポート番号を入力してください (デフォルト: {port}): ")
        if port_input.strip():
            port = int(port_input)
    except ValueError:
        print(f"⚠️ 無効なポート番号です。デフォルトの {port} を使用します。")
    
    # アプリケーションの実行
    run_app(port)

if __name__ == "__main__":
    main()
