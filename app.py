import os
import tempfile
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename

# Google Colabの環境かどうかをチェック
try:
    from google.colab import userdata
    # Google Colabのシークレット機能からAPIキーを取得
    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
    os.environ["DEEPGRAM_API_KEY"] = os.environ.get("DEEPGRAM_API_KEY", "")
    os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY", "")
    os.environ["AZURE_OPENAI_KEY"] = os.environ.get("AZURE_OPENAI_KEY", "")
    os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    os.environ["AZURE_OPENAI_DEPLOYMENT"] = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    os.environ["AZURE_OPENAI_API_VERSION"] = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
    print("Google Colab環境で実行しています。シークレット機能からAPIキーを読み込みました。")
except ImportError:
    print("ローカル環境で実行しています。.envファイルからAPIキーを読み込みました。")

# 各モジュールのインポート
from modules.transcription import transcribe_audio
from modules.llm_processing import summarize_text, question_answering
from modules.template_handler import process_template
from modules.file_handler import save_uploaded_file, get_file_path
from modules.download_handler import generate_download

app = Flask(__name__)

# アップロードされたファイルの保存先
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ファイルサイズ制限 (例: 100MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """ファイルアップロード処理"""
    if 'audio_file' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400
    
    audio_file = request.files['audio_file']
    template_file = request.files.get('template_file')
    
    if audio_file.filename == '':
        return jsonify({'error': '音声ファイルが選択されていません'}), 400
    
    # 音声ファイルを保存
    audio_path = save_uploaded_file(audio_file, app.config['UPLOAD_FOLDER'])
    
    # テンプレートファイルがあれば保存
    template_path = None
    if template_file and template_file.filename != '':
        template_path = save_uploaded_file(template_file, app.config['UPLOAD_FOLDER'])
    
    return jsonify({
        'status': 'success',
        'audio_path': audio_path,
        'template_path': template_path
    })
@app.route('/transcribe', methods=['POST'])
def transcribe():
    """音声文字起こし処理"""
    print("===== 文字起こし処理を開始 =====")
    data = request.json
    print(f"リクエストデータ: {data}")
    
    audio_path = data.get('audio_path')
    api_choice = data.get('api_choice', 'deepgram')  # デフォルトはDeepgram
    
    print(f"音声パス: {audio_path}")
    print(f"API選択: {api_choice}")
    
    if not audio_path:
        print("エラー: 音声ファイルのパスが指定されていません")
        return jsonify({'error': '音声ファイルのパスが指定されていません'}), 400
    
    try:
        # 完全なパスを取得
        full_path = get_file_path(audio_path)
        print(f"解決されたファイルパス: {full_path}")
        print(f"ファイルの存在確認: {os.path.exists(full_path)}")
        
        # 文字起こし実行
        print(f"文字起こし開始: {api_choice}")
        transcription = transcribe_audio(
            full_path, 
            api_choice=api_choice
        )
        print("文字起こし完了")
        
        return jsonify({
            'status': 'success',
            'transcription': transcription
        })
    
    except Exception as e:
        import traceback
        print(f"文字起こし処理中にエラーが発生しました: {str(e)}")
        print("詳細なエラー情報:")
        traceback.print_exc()
        return jsonify({'error': f'文字起こし処理中にエラーが発生しました: {str(e)}'}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    """文字起こしテキストの要約処理"""
    data = request.json
    text = data.get('text')
    api_choice = data.get('api_choice', 'azure')  # デフォルトはAzure OpenAI
    method = data.get('method', 'refine')  # デフォルトはrefine
    
    print(f"要約リクエスト: API={api_choice}, 方法={method}")
    print(f"Azure OpenAI設定: エンドポイント={os.environ.get('AZURE_OPENAI_ENDPOINT')[:10]}..., キー={os.environ.get('AZURE_OPENAI_KEY')[:5]}...")
    print(f"Groq設定: キー={os.environ.get('GROQ_API_KEY')[:5]}...")
    
    if not text:
        return jsonify({'error': 'テキストが指定されていません'}), 400
    
    try:
        # 要約実行
        print("要約処理を開始します...")
        summary = summarize_text(
            text, 
            api_choice=api_choice,
            method=method
        )
        print("要約処理が完了しました")
        
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    
    except Exception as e:
        import traceback
        print(f"要約処理中にエラーが発生しました: {str(e)}")
        print("詳細なエラー情報:")
        traceback.print_exc()
        return jsonify({'error': f'要約処理中にエラーが発生しました: {str(e)}'}), 500
@app.route('/qa', methods=['POST'])
def qa():
    """質疑応答処理"""
    data = request.json
    text = data.get('text')
    question = data.get('question')
    api_choice = data.get('api_choice', 'azure')  # デフォルトはAzure OpenAI
    
    if not text or not question:
        return jsonify({'error': 'テキストまたは質問が指定されていません'}), 400
    
    try:
        # 質疑応答実行
        answer = question_answering(
            text, 
            question,
            api_choice=api_choice
        )
        
        return jsonify({
            'status': 'success',
            'answer': answer
        })
    
    except Exception as e:
        return jsonify({'error': f'質疑応答処理中にエラーが発生しました: {str(e)}'}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """議事録生成処理"""
    data = request.json
    transcription = data.get('transcription')
    summary = data.get('summary')
    qa_data = data.get('qa_data', [])
    template_path = data.get('template_path')
    
    if not transcription:
        return jsonify({'error': '文字起こしデータがありません'}), 400
    
    try:
        # テンプレートがある場合は処理
        if template_path:
            report_path = process_template(
                get_file_path(template_path),
                transcription=transcription,
                summary=summary,
                qa_data=qa_data
            )
        else:
            # テンプレートがない場合は単純なテキスト出力
            report_path = generate_download(
                transcription, 
                summary, 
                qa_data,
                output_format='txt'
            )
        
        return jsonify({
            'status': 'success',
            'report_path': report_path
        })
    
    except Exception as e:
        return jsonify({'error': f'議事録生成中にエラーが発生しました: {str(e)}'}), 500

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    """ファイルダウンロード処理"""
    try:
        return send_file(
            get_file_path(filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': f'ダウンロード処理中にエラーが発生しました: {str(e)}'}), 500

if __name__ == '__main__':
    # Google Colab環境で実行されているかを確認
    try:
        import google.colab
        is_colab = True
    except:
        is_colab = False
    
    if is_colab:
        from google.colab.output import eval_js
        print("Google Colab環境で実行中です")
        # Colabでのポート公開処理
        PORT = 8000
        print(f"サーバーを起動します (ポート: {PORT})")
        app.run(host='0.0.0.0', port=PORT)
    else:
        # ローカル環境での実行
        app.run(debug=True)
