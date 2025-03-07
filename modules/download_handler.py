import os
import json
import docx
from datetime import datetime

def generate_download(transcription, summary=None, qa_data=None, output_format='docx'):
    """
    ダウンロード用のファイルを生成する
    
    Args:
        transcription (str): 文字起こしテキスト
        summary (str): 要約テキスト
        qa_data (list): 質疑応答データのリスト
        output_format (str): 出力フォーマット ('docx', 'txt', 'json')
        
    Returns:
        str: 生成されたファイルのパス
    """
    # 出力ディレクトリを確保
    output_dir = 'static/uploads'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # タイムスタンプを生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_format.lower() == 'docx':
        return generate_docx(transcription, summary, qa_data, output_dir, timestamp)
    elif output_format.lower() == 'txt':
        return generate_txt(transcription, summary, qa_data, output_dir, timestamp)
    elif output_format.lower() == 'json':
        return generate_json(transcription, summary, qa_data, output_dir, timestamp)
    else:
        raise ValueError(f"サポートされていない出力フォーマット: {output_format}")

def generate_docx(transcription, summary, qa_data, output_dir, timestamp):
    """
    Wordドキュメントを生成
    
    Args:
        transcription (str): 文字起こしテキスト
        summary (str): 要約テキスト
        qa_data (list): 質疑応答データのリスト
        output_dir (str): 出力ディレクトリ
        timestamp (str): タイムスタンプ
        
    Returns:
        str: 生成されたファイルのパス
    """
    # 新しいドキュメントを作成
    doc = docx.Document()
    
    # タイトルを追加
    doc.add_heading('音声文字起こし報告書', 0)
    
    # 生成日時を追加
    doc.add_paragraph(f'生成日時: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')
    
    # 要約セクションを追加（存在する場合）
    if summary:
        doc.add_heading('要約', level=1)
        doc.add_paragraph(summary)
    
    # 文字起こしセクションを追加
    doc.add_heading('文字起こし全文', level=1)
    doc.add_paragraph(transcription)
    
    # Q&Aセクションを追加（存在する場合）
    if qa_data and len(qa_data) > 0:
        doc.add_heading('質疑応答', level=1)
        
        # Q&Aテーブルを作成
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        
        # ヘッダー行を設定
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "質問"
        hdr_cells[1].text = "回答"
        
        # ヘッダー行のスタイルを設定
        for i, cell in enumerate(hdr_cells):
            run = cell.paragraphs[0].runs[0]
            run.bold = True
        
        # Q&Aデータを追加
        for qa in qa_data:
            row_cells = table.add_row().cells
            row_cells[0].text = qa.get('question', '')
            row_cells[1].text = qa.get('answer', '')
    
    # ファイルを保存
    output_path = os.path.join(output_dir, f'report_{timestamp}.docx')
    doc.save(output_path)
    
    return os.path.join(os.path.basename(output_dir), f'report_{timestamp}.docx')

def generate_txt(transcription, summary, qa_data, output_dir, timestamp):
    """
    テキストファイルを生成
    
    Args:
        transcription (str): 文字起こしテキスト
        summary (str): 要約テキスト
        qa_data (list): 質疑応答データのリスト
        output_dir (str): 出力ディレクトリ
        timestamp (str): タイムスタンプ
        
    Returns:
        str: 生成されたファイルのパス
    """
    content = []
    
    # タイトルを追加
    content.append("音声文字起こし報告書")
    content.append("="*40)
    
    # 生成日時を追加
    content.append(f'生成日時: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')
    content.append("")
    
    # 要約セクションを追加（存在する場合）
    if summary:
        content.append("【要約】")
        content.append("-"*40)
        content.append(summary)
        content.append("")
    
    # 文字起こしセクションを追加
    content.append("【文字起こし全文】")
    content.append("-"*40)
    content.append(transcription)
    content.append("")
    
    # Q&Aセクションを追加（存在する場合）
    if qa_data and len(qa_data) > 0:
        content.append("【質疑応答】")
        content.append("-"*40)
        
        for i, qa in enumerate(qa_data, 1):
            content.append(f"Q{i}: {qa.get('question', '')}")
            content.append(f"A{i}: {qa.get('answer', '')}")
            content.append("")
    
    # ファイルを保存
    output_path = os.path.join(output_dir, f'report_{timestamp}.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return os.path.join(os.path.basename(output_dir), f'report_{timestamp}.txt')

def generate_json(transcription, summary, qa_data, output_dir, timestamp):
    """
    JSONファイルを生成
    
    Args:
        transcription (str): 文字起こしテキスト
        summary (str): 要約テキスト
        qa_data (list): 質疑応答データのリスト
        output_dir (str): 出力ディレクトリ
        timestamp (str): タイムスタンプ
        
    Returns:
        str: 生成されたファイルのパス
    """
    # JSONデータを作成
    data = {
        'timestamp': datetime.now().isoformat(),
        'transcription': transcription,
        'summary': summary if summary else "",
        'qa_data': qa_data if qa_data else []
    }
    
    # ファイルを保存
    output_path = os.path.join(output_dir, f'report_{timestamp}.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return os.path.join(os.path.basename(output_dir), f'report_{timestamp}.json')
