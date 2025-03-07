import os
import tempfile
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def process_template(template_path, transcription=None, summary=None, qa_data=None):
    """
    Wordテンプレートを処理し、文字起こしや要約データを挿入する
    
    Args:
        template_path (str): テンプレートファイルのパス
        transcription (str): 文字起こしテキスト
        summary (str): 要約テキスト
        qa_data (list): 質疑応答データのリスト
        
    Returns:
        str: 生成された文書のパス
    """
    try:
        # テンプレートを読み込む
        doc = docx.Document(template_path)
        
        # テーブル内の特定のセルを探して内容を置き換える
        if summary:
            replace_table_content(doc, "{{summary}}", summary)
        
        if transcription:
            replace_table_content(doc, "{{transcription}}", transcription)
        
        # Q&Aデータがある場合はテーブルに追加
        if qa_data:
            add_qa_table(doc, qa_data)
        
        # 一時ファイルとして保存
        output_dir = 'static/uploads'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_path = os.path.join(output_dir, 'meeting_minutes.docx')
        doc.save(output_path)
        
        return output_path
    
    except Exception as e:
        raise Exception(f"テンプレート処理中にエラーが発生しました: {str(e)}")

def replace_table_content(doc, placeholder, content):
    """
    テーブル内のプレースホルダーを内容で置き換える
    
    Args:
        doc (Document): docxドキュメント
        placeholder (str): 置換対象のプレースホルダー
        content (str): 置換する内容
    """
    # すべてのテーブルを検索
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if placeholder in cell.text:
                    # セルの内容を置き換える
                    cell.text = cell.text.replace(placeholder, "")
                    
                    # パラグラフを追加
                    paragraph = cell.add_paragraph(content)
                    
                    # スタイルを適用（必要に応じて）
                    for run in paragraph.runs:
                        run.font.size = Pt(10)

def add_qa_table(doc, qa_data):
    """
    Q&Aテーブルをドキュメントに追加
    
    Args:
        doc (Document): docxドキュメント
        qa_data (list): 質疑応答データのリスト
    """
    # Q&Aセクションヘッダーを追加
    doc.add_heading("質疑応答", level=2)
    
    # Q&Aテーブルを作成
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    
    # ヘッダー行を設定
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "質問"
    hdr_cells[1].text = "回答"
    
    # ヘッダー行のスタイルを設定
    for cell in hdr_cells:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
    
    # Q&Aデータを追加
    for qa in qa_data:
        row_cells = table.add_row().cells
        row_cells[0].text = qa.get('question', '')
        row_cells[1].text = qa.get('answer', '')
