import os
import textwrap
import tiktoken
import requests
from openai import AzureOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import AzureChatOpenAI
# Groq用のインポートを変更
from langchain_groq import ChatGroq
# PromptTemplateのインポートを追加
from langchain_core.prompts import PromptTemplate

# 最大トークン数
MAX_TOKENS = 4000

def split_text(text):
    """
    テキストを処理可能なチャンクに分割する
    
    Args:
        text (str): 分割するテキスト
        
    Returns:
        list: 分割されたテキストのリスト
    """
    # テキストの長さに基づいてチャンクサイズを調整
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_TOKENS,
        chunk_overlap=200,
    )
    
    return text_splitter.split_text(text)

def get_azure_llm():
    """Azure OpenAIのLLMを取得"""
    api_key = os.environ.get("AZURE_OPENAI_KEY")
    api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")  # デフォルトバージョンを設定
    
    if not api_key or not api_endpoint:
        raise Exception(f"Azure OpenAI APIの設定が不足しています: キー={bool(api_key)}, エンドポイント={bool(api_endpoint)}")
    
    # デプロイメント名のチェック
    deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")  # デフォルト名
    
    print(f"Azure OpenAI設定: エンドポイント={api_endpoint}, バージョン={api_version}, デプロイメント={deployment_name}")
    
    return AzureChatOpenAI(
        openai_api_key=api_key,
        azure_endpoint=api_endpoint,
        azure_deployment=deployment_name,
        api_version=api_version,  # API バージョンを追加
        temperature=0.5
    )
def get_groq_llm(model_type):
    """Groq APIのLLMを取得"""
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise Exception("Groq APIキーが設定されていません")
    
    # モデルタイプに基づいてモデル名を選択
    if model_type == "llama3":
        model_name = "llama-3.3-70b-versatile"
    elif model_type == "gemma2":
        model_name = "gemma2-9b-it"
    else:
        model_name = "llama-3.3-70b-versatile"  # デフォルト
    
    return ChatGroq(
        api_key=api_key,
        model_name=model_name,
        temperature=0.5
    )
def summarize_text(text, api_choice='azure', method='refine', model_type='llama3'):
    """
    テキストを要約する
    
    Args:
        text (str): 要約するテキスト
        api_choice (str): 使用するAPI ('azure' または 'groq')
        method (str): 要約方法 ('map_reduce' または 'refine')
        model_type (str): Groq使用時のモデルタイプ ('llama3' または 'gemma2')
        
    Returns:
        str: 要約テキスト
    """
    try:
        # テキストを分割
        docs = split_text(text)
        
        # ドキュメント形式に変換
        from langchain_core.documents import Document
        docs = [Document(page_content=t) for t in docs]
        
        # プロンプトテンプレート
        map_template = """次の文書を要約してください:
        {text}
        
        簡潔で情報量の多い要約を日本語で作成してください。
        """
        
        map_prompt = PromptTemplate.from_template(map_template)
        
        combine_template = """次の要約をより簡潔にまとめてください:
        {text}
        
        全体の内容を網羅した簡潔で情報量の多い要約を日本語で作成してください。
        """
        
        combine_prompt = PromptTemplate.from_template(combine_template)
        
        # LLMを選択
        llm = None
        try:
            if api_choice.lower() == 'azure':
                print("Azure OpenAI APIを使用します")
                llm = get_azure_llm()
            elif api_choice.lower() == 'groq':
                print(f"Groq APIを使用します (モデル: {model_type})")
                llm = get_groq_llm(model_type)
            else:
                raise ValueError(f"不明なAPI選択: {api_choice}")
        except Exception as llm_error:
            print(f"選択されたAPI ({api_choice}) の初期化に失敗しました: {str(llm_error)}")
            print("代替APIを試行します...")
            
            # フォールバックオプション
            if llm is None:
                # もう一方のAPIを試す
                try:
                    if api_choice.lower() == 'azure':
                        print("フォールバック: Groq APIを使用します")
                        llm = get_groq_llm('llama3')
                    else:
                        print("フォールバック: Azure OpenAI APIを使用します")
                        llm = get_azure_llm()
                except Exception as fallback_error:
                    print(f"フォールバックAPIの初期化にも失敗しました: {str(fallback_error)}")
            
            if llm is None:
                raise Exception("利用可能なLLMがありません。APIキーの設定を確認してください。")
        
        # 要約チェーンを作成
        print(f"要約方法: {method}")
        if method == 'map_reduce':
            chain = load_summarize_chain(
                llm,
                chain_type="map_reduce",
                map_prompt=map_prompt,
                combine_prompt=combine_prompt,
                verbose=True
            )
        else:  # refine
            chain = load_summarize_chain(
                llm,
                chain_type="refine",
                verbose=True
            )
        
        # 要約を実行
        print("要約チェーンを実行します...")
        result = chain.invoke(docs)
        print("要約が完了しました")
        
        summary = result['output_text']
        
        # 英語で出力された場合は日本語に翻訳
        summary = translate_to_japanese(summary, api_choice)
        
        return summary
    
    except Exception as e:
        import traceback
        print("要約処理中にエラーが発生しました:")
        traceback.print_exc()
        raise Exception(f"要約処理中にエラーが発生しました: {str(e)}")

def question_answering(text, question, api_choice='azure', model_type='llama3'):
    """
    テキストに基づいて質問に回答する
    
    Args:
        text (str): 文脈テキスト
        question (str): 質問テキスト
        api_choice (str): 使用するAPI ('azure' または 'groq')
        model_type (str): Groq使用時のモデルタイプ ('llama3' または 'gemma2')
        
    Returns:
        str: 回答テキスト
    """
    try:
        # テキストを分割
        docs = split_text(text)
        
        # ドキュメント形式に変換
        from langchain_core.documents import Document
        docs = [Document(page_content=t) for t in docs]
        
        # LLMを選択
        llm = None
        try:
            if api_choice.lower() == 'azure':
                print("Azure OpenAI APIを使用します")
                llm = get_azure_llm()
            elif api_choice.lower() == 'groq':
                print(f"Groq APIを使用します (モデル: {model_type})")
                llm = get_groq_llm(model_type)
            else:
                raise ValueError(f"不明なAPI選択: {api_choice}")
        except Exception as llm_error:
            print(f"選択されたAPI ({api_choice}) の初期化に失敗しました: {str(llm_error)}")
            print("代替APIを試行します...")
            
            # フォールバックオプション
            if llm is None:
                # もう一方のAPIを試す
                try:
                    if api_choice.lower() == 'azure':
                        print("フォールバック: Groq APIを使用します")
                        llm = get_groq_llm('llama3')
                    else:
                        print("フォールバック: Azure OpenAI APIを使用します")
                        llm = get_azure_llm()
                except Exception as fallback_error:
                    print(f"フォールバックAPIの初期化にも失敗しました: {str(fallback_error)}")
            
            if llm is None:
                raise Exception("利用可能なLLMがありません。APIキーの設定を確認してください。")
        
        # QAチェーンを作成
        prompt_template = """以下のコンテキストを使用して、質問に回答してください。
        
        コンテキスト:
        {context}
        
        質問:
        {question}
        
        回答: 
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        chain = load_qa_chain(
            llm,
            chain_type="stuff",
            prompt=prompt
        )
        
        # 回答を取得
        print("質疑応答チェーンを実行します...")
        result = chain.invoke({
            "input_documents": docs,
            "question": question
        })
        print("質疑応答が完了しました")
        
        answer = result['output_text']
        
        # 英語で出力された場合は日本語に翻訳
        answer = translate_to_japanese(answer, api_choice)
        
        return answer
    
    except Exception as e:
        import traceback
        print("質疑応答処理中にエラーが発生しました:")
        traceback.print_exc()
        raise Exception(f"質疑応答処理中にエラーが発生しました: {str(e)}")

def translate_to_japanese(text, api_choice='azure'):
    """
    英語のテキストを日本語に翻訳する
    
    Args:
        text (str): 翻訳するテキスト
        api_choice (str): 使用するAPI ('azure' または 'groq')
        
    Returns:
        str: 翻訳されたテキスト
    """
    # 既に日本語の場合はそのまま返す
    import re
    # 日本語文字が含まれているかチェック（ひらがな、カタカナ、漢字）
    if re.search(r'[ぁ-んァ-ヶ一-龯]', text):
        # 日本語の文字が20%以上含まれていれば日本語と判断
        japanese_chars = len(re.findall(r'[ぁ-んァ-ヶ一-龯]', text))
        if japanese_chars / len(text) > 0.2:
            print("テキストは既に日本語です")
            return text
    
    try:
        print("英語から日本語への翻訳を開始します...")
        
        # LLMを選択
        llm = None
        try:
            if api_choice.lower() == 'azure':
                print("Azure OpenAI APIを使用します")
                llm = get_azure_llm()
            else:
                print("Groq APIを使用します")
                llm = get_groq_llm('llama3')
        except Exception as llm_error:
            print(f"選択されたAPI ({api_choice}) の初期化に失敗しました: {str(llm_error)}")
            print("代替APIを試行します...")
            
            # フォールバックオプション
            if api_choice.lower() == 'azure':
                print("フォールバック: Groq APIを使用します")
                llm = get_groq_llm('llama3')
            else:
                print("フォールバック: Azure OpenAI APIを使用します")
                llm = get_azure_llm()
        
        # 翻訳プロンプトの作成
        from langchain_core.prompts import PromptTemplate
        translate_template = """
        以下の英語のテキストを自然で読みやすい日本語に翻訳してください。
        内容を損なわず、日本語として自然な表現を使ってください。
        
        テキスト:
        {text}
        
        日本語訳:
        """
        
        translate_prompt = PromptTemplate.from_template(translate_template)
        
        # 翻訳を実行
        from langchain_core.output_parsers import StrOutputParser
        from langchain.chains import LLMChain
        
        chain = LLMChain(
            llm=llm,
            prompt=translate_prompt,
            output_parser=StrOutputParser()
        )
        
        translated_text = chain.run(text=text)
        print("翻訳が完了しました")
        
        return translated_text
    
    except Exception as e:
        import traceback
        print("翻訳処理中にエラーが発生しました:")
        traceback.print_exc()
        print(f"翻訳に失敗しました。元のテキストを返します: {str(e)}")
        return text  # エラーの場合は元のテキストを返す
