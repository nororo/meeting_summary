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
        print(f"テンプレート処理開始: {template_path}")
        print(f"テンプレートファイルの存在確認: {os.path.exists(template_path)}")
        
        # テンプレートを読み込む
        doc = docx.Document(template_path)
        
        # テンプレートの構造を分析
        print("\n===== テンプレート構造の分析 =====")
        print(f"段落数: {len(doc.paragraphs)}")
        print(f"テーブル数: {len(doc.tables)}")
        
        # 各テーブルの構造を表示
        for i, table in enumerate(doc.tables):
            print(f"\nテーブル {i+1}: {len(table.rows)}行 x {len(table.columns)}列")
            for row_idx, row in enumerate(table.rows):
                for col_idx, cell in enumerate(row.cells):
                    cell_text = cell.text.strip()
                    if "{{" in cell_text and "}}" in cell_text:
                        print(f"  プレースホルダー発見: 行{row_idx+1}, 列{col_idx+1} - '{cell_text}'")
        
        # 段落内のプレースホルダーを確認
        placeholders_in_paragraphs = []
        for i, para in enumerate(doc.paragraphs):
            if "{{" in para.text and "}}" in para.text:
                print(f"段落 {i+1} にプレースホルダーがあります: '{para.text}'")
                placeholders_in_paragraphs.append(para.text)
        
        print("===== テンプレート分析終了 =====\n")
        
        # テーブル内の特定のセルを探して内容を置き換える
        if summary:
            print("要約データを挿入")
            replace_table_content(doc, "{{summary}}", summary)
        
        if transcription:
            print("文字起こしデータを挿入")
            replace_table_content(doc, "{{transcription}}", transcription)
        
        # Q&Aデータがある場合はテーブルに追加
        if qa_data:
            print(f"Q&Aデータを挿入 ({len(qa_data)}件)")
            add_qa_table(doc, qa_data)
        
        # タイムスタンプを生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 出力ファイル名と保存先を設定
        output_filename = f'minutes_{timestamp}.docx'
        
        # 出力ディレクトリを確保
        output_dir = 'static/uploads'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 絶対パスと相対パスを生成
        try:
            # 現在のファイルの場所を基準にする
            base_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(base_dir)
            abs_output_path = os.path.join(parent_dir, output_dir, output_filename)
        except:
            # 絶対パスの生成に失敗した場合は相対パスをそのまま使用
            abs_output_path = os.path.join(output_dir, output_filename)
        
        relative_output_path = os.path.join(output_dir, output_filename)
        
        print(f"出力ファイル情報:")
        print(f"  ファイル名: {output_filename}")
        print(f"  絶対パス: {abs_output_path}")
        print(f"  相対パス: {relative_output_path}")
        
        # 処理後のテンプレート構造を確認
        print("\n===== 処理後のドキュメント確認 =====")
        placeholders_remaining = []
        for i, table in enumerate(doc.tables):
            for row in table.rows:
                for cell in row.cells:
                    if "{{" in cell.text and "}}" in cell.text:
                        print(f"  警告: テーブル {i+1} にプレースホルダーが残っています: '{cell.text}'")
                        placeholders_remaining.append(cell.text)
        
        for i, para in enumerate(doc.paragraphs):
            if "{{" in para.text and "}}" in para.text:
                print(f"  警告: 段落 {i+1} にプレースホルダーが残っています: '{para.text}'")
                placeholders_remaining.append(para.text)
        
        if placeholders_remaining:
            print(f"  未処理のプレースホルダーが {len(placeholders_remaining)}個 見つかりました")
        else:
            print("  すべてのプレースホルダーが正常に処理されました")
        print("===== ドキュメント確認終了 =====\n")
        
        # 文書を保存
        doc.save(abs_output_path)
        print(f"テンプレート処理完了: {abs_output_path}")
        
        # 保存したファイルの存在確認
        print(f"生成されたファイルの存在確認: {os.path.exists(abs_output_path)}")
        
        return relative_output_path
    
    except Exception as e:
        import traceback
        print(f"テンプレート処理中にエラーが発生しました: {str(e)}")
        traceback.print_exc()
        raise Exception(f"テンプレート処理中にエラーが発生しました: {str(e)}")

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


def replace_table_content(doc, placeholder, content):
    """
    テーブル内のプレースホルダーを内容で置き換える
    
    Args:
        doc (Document): docxドキュメント
        placeholder (str): 置換対象のプレースホルダー
        content (str): 置換する内容
    """
    print(f"プレースホルダー '{placeholder}' の置換を開始")
    replaced = False
    
    # すべてのテーブルを検索
    for table_idx, table in enumerate(doc.tables):
        for row_idx, row in enumerate(table.rows):
            for cell_idx, cell in enumerate(row.cells):
                if placeholder in cell.text:
                    print(f"プレースホルダーを発見: テーブル {table_idx+1}, 行 {row_idx+1}, セル {cell_idx+1}")
                    
                    # セルのすべてのパラグラフをクリア
                    for p in cell.paragraphs:
                        # 既存のパラグラフからプレースホルダーを削除
                        if placeholder in p.text:
                            p.text = p.text.replace(placeholder, "")
                    
                    # コンテンツを複数行に分割
                    content_lines = content.split('\n')
                    
                    # 最初の行は既存のパラグラフに追加（あれば）
                    if cell.paragraphs and content_lines:
                        first_line = content_lines[0]
                        cell.paragraphs[0].add_run(first_line)
                        content_lines = content_lines[1:]  # 最初の行を削除
                    
                    # 残りの行は新しいパラグラフとして追加
                    for line in content_lines:
                        p = cell.add_paragraph()
                        p.add_run(line)
                    
                    replaced = True
                    print(f"プレースホルダーを '{content[:30]}...' に置換しました")
    
    # テーブル以外の本文も検索（必要に応じて）
    for para in doc.paragraphs:
        if placeholder in para.text:
            print(f"本文内でプレースホルダーを発見")
            para.text = para.text.replace(placeholder, content)
            replaced = True
            print(f"本文内のプレースホルダーを置換しました")
    
    if not replaced:
        print(f"警告: プレースホルダー '{placeholder}' が見つかりませんでした")
