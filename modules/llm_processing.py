import os
import textwrap
import tiktoken
import requests
from openai import AzureOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import AzureChatOpenAI, ChatGroq
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
    
    if not api_key or not api_endpoint:
        raise Exception("Azure OpenAI APIの設定が不足しています")
    
    return AzureChatOpenAI(
        openai_api_key=api_key,
        azure_endpoint=api_endpoint,
        azure_deployment="gpt-4-turbo",
        temperature=0.5
    )

def get_groq_llm(model_type):
    """Groq APIのLLMを取得"""
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise Exception("Groq APIキーが設定されていません")
    
    # モデルタイプに基づいてモデル名を選択
    if model_type == "llama3":
        model_name = "llama3-8b-8192"
    elif model_type == "gemma2":
        model_name = "gemma-7b-it"
    else:
        model_name = "llama3-8b-8192"  # デフォルト
    
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
        
        # LLMを選択
        if api_choice.lower() == 'azure':
            llm = get_azure_llm()
        elif api_choice.lower() == 'groq':
            llm = get_groq_llm(model_type)
        else:
            raise ValueError(f"不明なAPI選択: {api_choice}")
        
        # プロンプトテンプレートを作成
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
        
        # 要約チェーンを作成
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
        result = chain.invoke(docs)
        
        return result['output_text']
    
    except Exception as e:
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
        if api_choice.lower() == 'azure':
            llm = get_azure_llm()
        elif api_choice.lower() == 'groq':
            llm = get_groq_llm(model_type)
        else:
            raise ValueError(f"不明なAPI選択: {api_choice}")
        
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
        result = chain.invoke({
            "input_documents": docs,
            "question": question
        })
        
        return result['output_text']
    
    except Exception as e:
        raise Exception(f"質疑応答処理中にエラーが
