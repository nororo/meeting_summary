##
# author   : Claude 3.7 Sonnet
# created  : 2025/03/07 15:33:00
##

import os
import logging
from typing import Optional, Dict, Any

from ..api.deepgram_client import DeepgramClient
from ..api.groq_client import GroqClient

logger = logging.getLogger(__name__)

class TranscriptionService:
    """
    音声ファイルの文字起こしを行うサービス
    
    複数の文字起こしAPIに対応し、設定に基づいて適切なAPIを使用します。
    """
    
    def __init__(self):
        self.deepgram_client = DeepgramClient()
        self.groq_client = GroqClient()
    
    def transcribe(
        self, 
        audio_file_path: str, 
        service: str = "deepgram", 
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        音声ファイルの文字起こしを実行
        
        Parameters:
        -----------
        audio_file_path : str
            文字起こし対象の音声ファイルパス
        service : str, optional
            使用する文字起こしサービス ('deepgram' または 'groq_whisper')
        options : Dict[str, Any], optional
            文字起こしの追加オプション
            
        Returns:
        --------
        str
            文字起こし結果のテキスト
        
        Raises:
        -------
        ValueError
            不正なサービス名や設定エラーの場合
        """
        if options is None:
            options = {}
        
        try:
            if service == "deepgram":
                return self._transcribe_with_deepgram(audio_file_path, options)
            elif service == "groq_whisper":
                return self._transcribe_with_groq_whisper(audio_file_path, options)
            else:
                raise ValueError(f"不明な文字起こしサービス: {service}")
        except Exception as e:
            logger.error(f"文字起こし中にエラーが発生しました: {str(e)}")
            raise
    
    def _transcribe_with_deepgram(self, audio_file_path: str, options: Dict[str, Any]) -> str:
        """
        Deepgram APIを使用して文字起こしを実行
        
        Parameters:
        -----------
        audio_file_path : str
            音声ファイルパス
        options : Dict[str, Any]
            Deepgram APIのオプション
            
        Returns:
        --------
        str
            文字起こし結果
        """
        # デフォルトオプションの設定
        default_options = {
            "language": "ja",  # 日本語
            "model": "general",
            "tier": "enhanced",
            "punctuate": True,
            "diarize": True,  # 話者分離
        }
        
        # ユーザー指定のオプションで上書き
        default_options.update(options)
        
        # Deepgramクライアントで文字起こし実行
        response = self.deepgram_client.transcribe_audio(audio_file_path, default_options)
        
        # レスポンスから文字起こしテキストを抽出
        try:
            transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
            return transcript
        except (KeyError, IndexError) as e:
            logger.error(f"Deepgramのレスポンス解析エラー: {str(e)}")
            if response and "error" in response:
                logger.error(f"Deepgramエラー詳細: {response['error']}")
            return ""
    
    def _transcribe_with_groq_whisper(self, audio_file_path: str, options: Dict[str, Any]) -> str:
        """
        Groq API (Whisper) を使用して文字起こしを実行
        
        Parameters:
        -----------
