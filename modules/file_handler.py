import os
import uuid
from werkzeug.utils import secure_filename

def save_uploaded_file(file_obj, upload_folder):
    """
    アップロードされたファイルを保存する
    
    Args:
        file_obj: ファイルオブジェクト
        upload_folder (str): アップロードフォルダのパス
        
    Returns:
        str: 保存されたファイルのパス
    """
    # 安全なファイル名を生成
    filename = secure_filename(file_obj.filename)
    
    # 拡張子を取得
    _, file_extension = os.path.splitext(filename)
    
    # ユニークなファイル名を生成
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 保存パスを作成
    file_path = os.path.join(upload_folder, unique_filename)
    
    # フォルダが存在しない場合は作成
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # ファイルを保存
    file_obj.save(file_path)
    
    # 相対パスを返す
    return os.path.join(os.path.basename(upload_folder), unique_filename)
def get_file_path(relative_path):
    """
    相対パスから完全なファイルパスを取得
    
    Args:
        relative_path (str): 相対ファイルパス
        
    Returns:
        str: 完全なファイルパス
    """
    # ベースディレクトリを取得
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # パスの修正：uploads/ を static/uploads/ に変換
    if relative_path.startswith('uploads/'):
        relative_path = 'static/' + relative_path
    
    # 完全なパスを生成
    if os.path.isabs(relative_path):
        full_path = relative_path
    else:
        full_path = os.path.join(base_dir, relative_path)
    
    # Colabの場合は /content ディレクトリも考慮
    if not os.path.exists(full_path):
        # Google Colabの場合は /content から始まるパスの可能性がある
        colab_path = os.path.join('/content', 'meeting_summary', relative_path)
        if os.path.exists(colab_path):
            return colab_path
            
        # static/uploads が含まれていない場合の対応
        if 'static/uploads' not in relative_path and 'uploads/' in relative_path:
            alternative_path = relative_path.replace('uploads/', 'static/uploads/')
            full_alt_path = os.path.join(base_dir, alternative_path)
            if os.path.exists(full_alt_path):
                return full_alt_path
                
            # Colab環境用の代替パス
            colab_alt_path = os.path.join('/content', 'meeting_summary', alternative_path)
            if os.path.exists(colab_alt_path):
                return colab_alt_path
    
        # それでも見つからない場合はエラー
        raise FileNotFoundError(f"ファイルが見つかりません: {full_path} (試したパス: {colab_path})")
    
    return full_path

def clean_temp_files(directory, max_age=3600):
    """
    一時ファイルを定期的にクリーンアップ
    
    Args:
        directory (str): クリーンアップするディレクトリ
        max_age (int): ファイルの最大年齢（秒）
    """
    import time
    
    current_time = time.time()
    
    # ディレクトリ内のすべてのファイルをチェック
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # ファイルの最終変更時間を取得
        file_mod_time = os.path.getmtime(file_path)
        
        # 最大年齢より古いファイルを削除
        if current_time - file_mod_time > max_age:
            try:
                os.remove(file_path)
                print(f"古いファイルを削除しました: {file_path}")
            except Exception as e:
                print(f"ファイル削除中にエラーが発生しました: {str(e)}")
