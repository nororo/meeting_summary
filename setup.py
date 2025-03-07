import os
import sys
import subprocess

def setup_environment():
    """アプリケーション実行に必要な環境をセットアップする"""
    
    print("🔧 アプリケーション環境のセットアップを開始します...")
    
    # Google Colab環境かどうかを確認
    try:
        import google.colab
        is_colab = True
        print("✓ Google Colab環境を検出しました")
    except ImportError:
        is_colab = False
        print("✓ ローカル環境で実行します")
    
    # 必要なディレクトリを作成
    print("📁 必要なディレクトリを作成中...")
    directories = ['static', 'static/uploads', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  ✓ {directory} ディレクトリを作成しました")
        else:
            print(f"  ✓ {directory} ディレクトリは既に存在します")
    
    # 依存関係をインストール
    print("📦 必要なパッケージをインストール中...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("  ✓ 必要なパッケージをインストールしました")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ パッケージのインストールに失敗しました: {e}")
        return False
    
    # ffmpegのインストール（Colabの場合）
    if is_colab:
        print("🔊 ffmpegをインストール中...")
        try:
            subprocess.check_call(["apt-get", "update", "-qq"])
            subprocess.check_call(["apt-get", "install", "-y", "-qq", "ffmpeg"])
            print("  ✓ ffmpegをインストールしました")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ ffmpegのインストールに失敗しました: {e}")
            print("  ⚠️ 音声ファイルの処理に問題が発生する可能性があります")
    
    # APIキーの確認
    if is_colab:
        try:
            from google.colab import userdata
            
            # 必要なAPIキーのリスト
            api_keys = [
                "OPENAI_API_KEY",
                "DEEPGRAM_API_KEY",
                "GROQ_API_KEY",
                "AZURE_OPENAI_KEY",
                "AZURE_OPENAI_ENDPOINT"
            ]
            
            missing_keys = []
            
            # APIキーが設定されているか確認
            print("🔑 APIキーの確認中...")
            for key in api_keys:
                try:
                    value = userdata.get(key)
                    if value:
                        print(f"  ✓ {key} が設定されています")
                    else:
                        print(f"  ❌ {key} が設定されていますが、値が空です")
                        missing_keys.append(key)
                except Exception:
                    print(f"  ❌ {key} が設定されていません")
                    missing_keys.append(key)
            
            # 不足しているAPIキーがある場合は警告
            if missing_keys:
                print("\n⚠️ 以下のAPIキーが不足しています:")
                for key in missing_keys:
                    print(f"  - {key}")
                print("\nGoogle Colabのシークレット機能を使用して、これらのAPIキーを設定してください。")
                print("参考: https://research.google.com/colaboratory/secrets/")
            
        except ImportError:
            print("❌ Google Colabのシークレット機能にアクセスできません")
    else:
        # ローカル環境の場合は.envファイルを確認
        if not os.path.exists('.env'):
            print("📝 .envファイルを作成します...")
            with open('.env', 'w') as f:
                f.write("""# API Keys
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
""")
            print("  ✓ .envファイルを作成しました。APIキーを設定してください。")
        else:
            print("✓ .envファイルが既に存在します")
    
    print("\n✅ セットアップが完了しました！")
    return True

if __name__ == "__main__":
    setup_environment()
