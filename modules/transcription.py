import os
import json
import time
import tempfile
from pydub import AudioSegment
import requests

# 音声ファイルの最大長さ（ミリ秒）- 例: 10分
MAX_AUDIO_LENGTH = 10 * 60 * 1000

def split_audio(audio_path):
    """
    長い音声ファイルを処理可能なチャンクに分割する
    
    Args:
        audio_path (str): 音声ファイルのパス
        
    Returns:
        list: 分割された一時音声ファイルのパスリスト
    """
    try:
        # 音声ファイルを読み込む
        audio = AudioSegment.from_file(audio_path)
        
        # ファイルが短い場合は分割不要
        if len(audio) <= MAX_AUDIO_LENGTH:
            return [audio_path]
        
        # 分割する
        chunks = []
        for i in range(0, len(audio), MAX_AUDIO_LENGTH):
            chunk = audio[i:i + MAX_AUDIO_LENGTH]
            
            # 一時ファイルを作成
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            chunk.export(temp_file.name, format="wav")
            chunks.append(temp_file.name)
        
        return chunks
    
    except Exception as e:
        raise Exception(f"音声分割中にエラーが発生しました: {str(e)}")

def transcribe_with_deepgram(audio_path):
    """
    Deepgram APIを使用して音声を文字起こしする
    
    Args:
        audio_path (str): 音声ファイルのパス
        
    Returns:
        str: 文字起こしテキスト
    """
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        raise Exception("Deepgram APIキーが設定されていません")
    
    try:
        # 音声ファイルを開く
        with open(audio_path, 'rb') as audio:
            # APIリクエストを送信
            response = requests.post(
                "https://api.deepgram.com/v1/listen?language=ja",
                headers={
                    "Authorization": f"Token {api_key}",
                    "Content-Type": "audio/wav"
                },
                data=audio
            )
        
        if response.status_code != 200:
            raise Exception(f"Deepgram APIエラー: {response.text}")
        
        # レスポンスからテキストを抽出
        result = response.json()
        return result['results']['channels'][0]['alternatives'][0]['transcript']
    
    except Exception as e:
        raise Exception(f"Deepgramでの文字起こし中にエラーが発生しました: {str(e)}")

def transcribe_with_groq(audio_path):
    """
    Groq Whisper APIを使用して音声を文字起こしする
    
    Args:
        audio_path (str): 音声ファイルのパス
        
    Returns:
        str: 文字起こしテキスト
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise Exception("Groq APIキーが設定されていません")
    
    try:
        with open(audio_path, 'rb') as audio:
            # APIリクエストを送信
            response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": audio},
                data={"model": "whisper-large-v3-turbo", "language": "ja"}
            )
        
        if response.status_code != 200:
            raise Exception(f"Groq APIエラー: {response.text}")
        
        # レスポンスからテキストを抽出
        result = response.json()
        return result['text']
    
    except Exception as e:
        raise Exception(f"Groq Whisperでの文字起こし中にエラーが発生しました: {str(e)}")

def transcribe_audio(audio_path, api_choice='deepgram'):
    """
    音声を文字起こしする
    
    Args:
        audio_path (str): 音声ファイルのパス
        api_choice (str): 使用するAPI ('deepgram' または 'groq')
        
    Returns:
        str: 文字起こしテキスト
    """
    try:
        # 音声ファイルを分割
        chunk_paths = split_audio(audio_path)
        
        # 各チャンクを文字起こし
        transcriptions = []
        for chunk_path in chunk_paths:
            if api_choice.lower() == 'deepgram':
                chunk_text = transcribe_with_deepgram(chunk_path)
            elif api_choice.lower() == 'groq':
                chunk_text = transcribe_with_groq(chunk_path)
            else:
                raise ValueError(f"不明なAPI選択: {api_choice}")
            
            transcriptions.append(chunk_text)
            
            # 一時ファイルを削除（元のファイル以外）
            if chunk_path != audio_path:
                os.unlink(chunk_path)
        
        # 結果を結合
        return " ".join(transcriptions)
    
    except Exception as e:
        raise Exception(f"文字起こし処理中にエラーが発生しました: {str(e)}")
