# test_transcription.py というファイル名で保存
!pip show pydub
!pip show ffmpeg-python
!which ffmpeg

import os
from modules.transcription import transcribe_with_deepgram

# テスト用の短い音声ファイルのパス
test_file = "/content/meeting_summary/tests/uploads/JUAS-20241031_161932-Meeting Recording.mp4"  # 実際のファイルパスに置き換えてください

try:
    # Deepgramでテスト
    result = transcribe_with_deepgram(test_file)
    print("文字起こし成功:")
    print(result)
except Exception as e:
    print(f"エラー発生: {str(e)}")
    # エラーの詳細情報
    import traceback
    traceback.print_exc()
